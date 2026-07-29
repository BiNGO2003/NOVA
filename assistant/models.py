from django.conf import settings
from django.db import models


class Task(models.Model):
    class Priority(models.TextChoices):
        HIGH = "high", "Высокий"
        MEDIUM = "medium", "Средний"
        LOW = "low", "Низкий"

    title = models.CharField("задача", max_length=240)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    completed = models.BooleanField(default=False)
    due_date = models.DateField("срок", null=True, blank=True)
    due_time = models.TimeField("время", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)

    class Meta:
        ordering = ["completed", "priority", "-created_at"]

    def __str__(self):
        return self.title


class Note(models.Model):
    text = models.TextField("заметка", max_length=1200)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.text[:60]


class Memory(models.Model):
    """Small, explicit facts NOVA may use in future planning."""
    key = models.CharField("тема", max_length=100)
    value = models.CharField("факт", max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memories", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.key}: {self.value}"


class Habit(models.Model):
    name = models.CharField("привычка", max_length=160)
    streak = models.PositiveIntegerField(default=0)
    last_completed_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits", null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
