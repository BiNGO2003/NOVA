import json
from datetime import date, time, timedelta
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from .models import Habit, Memory, Note, Task
from .research import research
from .services import nova_reply


def serialize(task):
    return {"id": task.id, "title": task.title, "priority": task.priority, "completed": task.completed, "due_date": task.due_date.isoformat() if task.due_date else None, "due_time": task.due_time.isoformat(timespec="minutes") if task.due_time else None}


@login_required
@ensure_csrf_cookie
def home(request):
    return render(request, "assistant/home.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "registration/signup.html", {"form": form})


@login_required
@require_GET
def tasks(request):
    return JsonResponse({"tasks": [serialize(task) for task in Task.objects.filter(user=request.user)]})


@login_required
@require_POST
def task_create(request):
    data = json.loads(request.body or "{}")
    title = (data.get("title") or "").strip()
    if not title:
        return JsonResponse({"error": "Укажите задачу."}, status=400)
    priority = data.get("priority", Task.Priority.MEDIUM)
    if priority not in Task.Priority.values:
        priority = Task.Priority.MEDIUM
    try:
        due_date = date.fromisoformat(data["due_date"]) if data.get("due_date") else None
        due_time = time.fromisoformat(data["due_time"]) if data.get("due_time") else None
    except ValueError:
        return JsonResponse({"error": "Дата или время имеют неверный формат."}, status=400)
    task = Task.objects.create(user=request.user, title=title, priority=priority, due_date=due_date, due_time=due_time)
    return JsonResponse({"task": serialize(task)}, status=201)


@login_required
@require_POST
def task_update(request, task_id):
    task = Task.objects.filter(id=task_id, user=request.user).first()
    if not task:
        return JsonResponse({"error": "Задача не найдена."}, status=404)
    data = json.loads(request.body or "{}")
    allowed = []
    if "completed" in data:
        task.completed = bool(data["completed"])
        allowed.append("completed")
    if "priority" in data and data["priority"] in Task.Priority.values:
        task.priority = data["priority"]
        allowed.append("priority")
    if allowed:
        task.save(update_fields=allowed)
    return JsonResponse({"task": serialize(task)})


@login_required
@require_POST
def task_delete(request, task_id):
    deleted, _ = Task.objects.filter(id=task_id, user=request.user).delete()
    return JsonResponse({"deleted": bool(deleted)})


@login_required
@require_POST
def command(request):
    data = json.loads(request.body or "{}")
    reply, payload = nova_reply(data.get("command", ""))
    result = research(data.get("command", "")) if payload.get("research") else {"sources": [], "medical": False}
    return JsonResponse({"reply": result.get("answer", reply), "focus": payload.get("focus"), "tasks": [serialize(task) for task in Task.objects.filter(user=request.user)], "sources": result["sources"], "medical": result["medical"]})


@login_required
@require_GET
def notes(request):
    return JsonResponse({"notes": [{"id": note.id, "text": note.text, "created_at": note.created_at.isoformat()} for note in Note.objects.filter(user=request.user)[:8]]})


@login_required
@require_POST
def note_create(request):
    data = json.loads(request.body or "{}")
    text = (data.get("text") or "").strip()
    if not text:
        return JsonResponse({"error": "Заметка пуста."}, status=400)
    note = Note.objects.create(user=request.user, text=text)
    return JsonResponse({"note": {"id": note.id, "text": note.text, "created_at": note.created_at.isoformat()}}, status=201)


@login_required
@require_POST
def note_delete(request, note_id):
    deleted, _ = Note.objects.filter(id=note_id, user=request.user).delete()
    return JsonResponse({"deleted": bool(deleted)})


@login_required
@require_GET
def memories(request):
    return JsonResponse({"memories": [{"id": memory.id, "key": memory.key, "value": memory.value} for memory in Memory.objects.filter(user=request.user)[:20]]})


@login_required
@require_POST
def memory_create(request):
    data = json.loads(request.body or "{}")
    key, value = (data.get("key") or "").strip(), (data.get("value") or "").strip()
    if not key or not value:
        return JsonResponse({"error": "Укажите тему и факт для памяти."}, status=400)
    memory = Memory.objects.create(user=request.user, key=key[:100], value=value[:500])
    return JsonResponse({"memory": {"id": memory.id, "key": memory.key, "value": memory.value}}, status=201)


@login_required
@require_POST
def memory_delete(request, memory_id):
    deleted, _ = Memory.objects.filter(id=memory_id, user=request.user).delete()
    return JsonResponse({"deleted": bool(deleted)})


@login_required
@require_GET
def habits(request):
    today = date.today()
    return JsonResponse({"habits": [{"id": habit.id, "name": habit.name, "streak": habit.streak, "done_today": habit.last_completed_on == today} for habit in Habit.objects.filter(user=request.user)]})


@login_required
@require_POST
def habit_create(request):
    data = json.loads(request.body or "{}")
    name = (data.get("name") or "").strip()
    if not name:
        return JsonResponse({"error": "Назовите привычку."}, status=400)
    habit = Habit.objects.create(user=request.user, name=name[:160])
    return JsonResponse({"habit": {"id": habit.id, "name": habit.name, "streak": habit.streak, "done_today": False}}, status=201)


@login_required
@require_POST
def habit_toggle(request, habit_id):
    habit = Habit.objects.filter(id=habit_id, user=request.user).first()
    if not habit:
        return JsonResponse({"error": "Привычка не найдена."}, status=404)
    today = date.today()
    if habit.last_completed_on == today:
        habit.last_completed_on = None
        habit.streak = max(0, habit.streak - 1)
    else:
        habit.streak = habit.streak + 1 if habit.last_completed_on == today - timedelta(days=1) else 1
        habit.last_completed_on = today
    habit.save(update_fields=["streak", "last_completed_on"])
    return JsonResponse({"habit": {"id": habit.id, "name": habit.name, "streak": habit.streak, "done_today": habit.last_completed_on == today}})


@login_required
@require_POST
def habit_delete(request, habit_id):
    deleted, _ = Habit.objects.filter(id=habit_id, user=request.user).delete()
    return JsonResponse({"deleted": bool(deleted)})
