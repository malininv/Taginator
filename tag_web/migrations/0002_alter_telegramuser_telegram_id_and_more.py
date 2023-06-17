# Generated by Django 4.2.2 on 2023-06-17 08:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tag_web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='telegram_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]