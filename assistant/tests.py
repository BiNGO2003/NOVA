from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from .models import Task


class NovaApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="planner", password="safe-password-123")
        self.client.force_login(self.user)

    def test_creates_task_from_api(self):
        response = self.client.post(reverse("task-create"), data='{"title":"Подготовить отчёт","priority":"high"}', content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.get().title, "Подготовить отчёт")

    def test_command_creates_task_in_nova_style(self):
        response = self.client.post(reverse("command"), data='{"command":"добавь задачу проверить бюджет"}', content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.get().title, "проверить бюджет")
        self.assertIn("Добавила", response.json()["reply"])

    def test_plan_command_has_next_step(self):
        Task.objects.create(user=self.user, title="Критичная задача", priority="high")
        response = self.client.post(reverse("command"), data='{"command":"покажи план"}', content_type="application/json")
        self.assertIn("Начните с первой высокой", response.json()["reply"])

    def test_task_accepts_date_and_time(self):
        response = self.client.post(reverse("task-create"), data='{"title":"Созвон","due_date":"2026-07-30","due_time":"14:30"}', content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["task"]["due_time"], "14:30")

    def test_creates_note(self):
        response = self.client.post(reverse("note-create"), data='{"text":"Проверить вводные перед встречей"}', content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["note"]["text"], "Проверить вводные перед встречей")

    @patch("assistant.views.research")
    def test_question_returns_sources_for_answer_window(self, mock_research):
        mock_research.return_value = {"answer": "Краткая справка.", "medical": False, "sources": [{"name": "Wikipedia", "url": "https://ru.wikipedia.org", "excerpt": "Фрагмент"}]}
        response = self.client.post(reverse("command"), data='{"command":"что такое фотосинтез"}', content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sources"][0]["name"], "Wikipedia")

    def test_note_can_be_deleted(self):
        created = self.client.post(reverse("note-create"), data='{"text":"Удалить меня"}', content_type="application/json").json()["note"]
        response = self.client.post(reverse("note-delete", args=[created["id"]]))
        self.assertTrue(response.json()["deleted"])

    def test_memory_and_habit_endpoints(self):
        memory = self.client.post(reverse("memory-create"), data='{"key":"Работа","value":"Предпочитаю утренние встречи"}', content_type="application/json")
        self.assertEqual(memory.status_code, 201)
        habit = self.client.post(reverse("habit-create"), data='{"name":"Прогулка"}', content_type="application/json").json()["habit"]
        completed = self.client.post(reverse("habit-toggle", args=[habit["id"]])).json()["habit"]
        self.assertTrue(completed["done_today"])
        self.assertEqual(completed["streak"], 1)

    def test_registration_creates_and_logs_in_user(self):
        self.client.logout()
        response = self.client.post(reverse("signup"), {"username": "new-user", "password1": "new-password-123", "password2": "new-password-123"})
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
