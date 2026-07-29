from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("assistant", "0003_merge_0002_alter_task_options_0002_task_due_time_note")]
    operations = [
        migrations.CreateModel(name="Habit", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=160, verbose_name="привычка")),
            ("streak", models.PositiveIntegerField(default=0)),
            ("last_completed_on", models.DateField(blank=True, null=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ["name"]}),
        migrations.CreateModel(name="Memory", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("key", models.CharField(max_length=100, verbose_name="тема")),
            ("value", models.CharField(max_length=500, verbose_name="факт")),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ["-created_at"]}),
    ]
