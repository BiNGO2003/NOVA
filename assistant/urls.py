from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("register/", views.signup, name="signup"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.home, name="home"),
    path("api/tasks/", views.tasks, name="tasks"),
    path("api/tasks/create/", views.task_create, name="task-create"),
    path("api/tasks/<int:task_id>/", views.task_update, name="task-update"),
    path("api/tasks/<int:task_id>/delete/", views.task_delete, name="task-delete"),
    path("api/command/", views.command, name="command"),
    path("api/notes/", views.notes, name="notes"),
    path("api/notes/create/", views.note_create, name="note-create"),
    path("api/notes/<int:note_id>/delete/", views.note_delete, name="note-delete"),
    path("api/memories/", views.memories, name="memories"),
    path("api/memories/create/", views.memory_create, name="memory-create"),
    path("api/memories/<int:memory_id>/delete/", views.memory_delete, name="memory-delete"),
    path("api/habits/", views.habits, name="habits"),
    path("api/habits/create/", views.habit_create, name="habit-create"),
    path("api/habits/<int:habit_id>/toggle/", views.habit_toggle, name="habit-toggle"),
    path("api/habits/<int:habit_id>/delete/", views.habit_delete, name="habit-delete"),
]
