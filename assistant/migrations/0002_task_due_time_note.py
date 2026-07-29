from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("assistant", "0001_initial")]
    operations = [
        migrations.AddField(model_name="task", name="due_time", field=models.TimeField(blank=True, null=True, verbose_name="время")),
        migrations.CreateModel(name="Note", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("text", models.TextField(max_length=1200, verbose_name="заметка")),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ["-created_at"]}),
    ]
