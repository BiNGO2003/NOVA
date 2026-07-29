from django.contrib import admin
from .models import Habit, Memory, Note, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "priority", "completed", "due_date", "created_at")
    list_filter = ("priority", "completed")
    search_fields = ("title",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_at")
    search_fields = ("text",)


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "created_at")
    search_fields = ("key", "value")


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "streak", "last_completed_on")
