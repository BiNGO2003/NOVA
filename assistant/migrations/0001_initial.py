from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Task", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("title", models.CharField(max_length=240, verbose_name="задача")),
        ("priority", models.CharField(choices=[("high", "Высокий"), ("medium", "Средний"), ("low", "Низкий")], default="medium", max_length=10)),
        ("completed", models.BooleanField(default=False)),
        ("due_date", models.DateField(blank=True, null=True, verbose_name="срок")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
    ])]
