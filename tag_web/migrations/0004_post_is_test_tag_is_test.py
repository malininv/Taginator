# Generated by Django 4.2.2 on 2023-06-21 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tag_web', '0003_rename_telegram_id_telegramuser_tg_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_test',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='is_test',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
