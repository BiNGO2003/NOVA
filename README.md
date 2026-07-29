# NOVA

Персональный ассистент для задач и фокус-сессий на Django.

## Запуск

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Откройте `http://127.0.0.1:8000/`.

## Запуск на Render

Start Command:

```text
gunicorn nova_project.wsgi:application
```

В проекте Django-пакет называется `nova_project`, поэтому `gunicorn config.wsgi:application` здесь не сработает: модуля `config` нет.

## Команды

- `добавь задачу подготовить отчёт`
- `покажи план`
- `готово 1`
- `фокус 25`
- `мотивация`

NOVA отвечает кратко и предлагает следующий логичный шаг. Для производственного использования установите собственный `SECRET_KEY`, выключите `DEBUG` и задайте `ALLOWED_HOSTS`.
