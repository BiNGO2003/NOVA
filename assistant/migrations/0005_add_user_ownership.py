from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("assistant", "0004_memory_habit"),
    ]

    operations = [
        migrations.AddField(model_name="task", name="user", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="note", name="user", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="notes", to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="memory", name="user", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="memories", to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="habit", name="user", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="habits", to=settings.AUTH_USER_MODEL)),
    ]
