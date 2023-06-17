from django.db import models
from django.contrib.auth.models import User

DEFAULT_TAG_NAME = 'Без тега'


class Post(models.Model):
    text = models.TextField(db_index=True)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, blank=True, related_name='posts')
    date_pub = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:20]

    class Meta:
        ordering = ['-date_pub']

    @property
    def date_pub_formatted(self):
        return self.date_pub.strftime('%d.%m.%Y %H:%M')


class Tag(models.Model):
    name = models.CharField(max_length=50, default=DEFAULT_TAG_NAME)
    telegram_user = models.ForeignKey('TelegramUser', blank=True, on_delete=models.CASCADE, related_name='tags')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name) + f' ({self.telegram_user})'


class TelegramUser(models.Model):
    tg_id = models.IntegerField(unique=True, blank=True, null=True)
    tg_first_name = models.CharField(max_length=200, blank=True, null=True)
    tg_last_name = models.CharField(max_length=200, blank=True, null=True)
    tg_username = models.CharField(max_length=200, blank=True, null=True)
    tg_photo_url = models.CharField(max_length=200, blank=True, null=True)
    tg_auth_date = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.tg_id} {self.tg_first_name} {self.tg_last_name}"

    @staticmethod
    def make_from_dict(data):
        user, created = TelegramUser.objects.get_or_create(tg_id=data.get('id', ''))
        user.tg_first_name = data.get('first_name', '')
        user.tg_last_name = data.get('last_name', '')
        user.tg_username = data.get('username', '')
        user.tg_photo_url = data.get('photo_url', '')
        user.tg_auth_date = data.get('auth_date', '')
        return user

