import re
from .models import Task


def nova_reply(command: str) -> tuple[str, dict]:
    """A concise, proactive command router for NOVA's Russian interface."""
    text = command.strip()
    lower = text.lower()
    if not text:
        return "Сэр, команда не поступила. Система предпочитает конкретику.", {}

    task_match = re.search(r"(?:добавь\s+)?задач[уа]?\s+(.+)", lower)
    if task_match:
        title = text[task_match.start(1):].strip()
        task = Task.objects.create(title=title)
        return f"Добавила задачу «{task.title}». По умолчанию — средний приоритет; при необходимости ужесточим режим.", {"task": task}

    completed_match = re.search(r"готово\s*(\d+)", lower)
    if completed_match:
        index = int(completed_match.group(1)) - 1
        active = list(Task.objects.filter(completed=False))
        if 0 <= index < len(active):
            task = active[index]
            task.completed = True
            task.save(update_fields=["completed"])
            return f"«{task.title}» отмечена выполненной. Ещё один повод не дать хаосу победить.", {"task": task}
        return "Такой активной задачи не вижу. Нумерация начинается с первого пункта, как и положено цивилизованной системе.", {}

    if "план" in lower or "сегодня" in lower:
        active = Task.objects.filter(completed=False).count()
        high = Task.objects.filter(completed=False, priority=Task.Priority.HIGH).count()
        return (f"Сегодня в работе {active} задач. Критичных — {high}. "
                + ("Начните с первой высокой: она даст наибольший эффект." if high else "Выберите одну задачу и включите фокус на 25 минут.")), {}
    if "мотивац" in lower or "совет" in lower:
        return "Не нужно выигрывать весь день прямо сейчас. Достаточно выиграть следующие 25 минут.", {}
    if "фокус" in lower:
        minutes = re.search(r"\d+", lower)
        value = minutes.group(0) if minutes else "25"
        return f"Фокус-сессия на {value} минут подготовлена. Уведомления можно считать временной формой саботажа.", {"focus": int(value)}
    return "Проверяю открытые источники и подготовлю короткую справку с ссылками.", {"research": True}
