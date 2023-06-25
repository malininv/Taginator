from django.db import models
from django.contrib.auth.models import AbstractUser
from asgiref.sync import sync_to_async

DEFAULT_TAG_NAME = 'Без тега'
DEFAULT_PASSWORD = 'Taginator_help_bot'
MAX_TAG_LENGTH = 48


class Post(models.Model):
    text = models.TextField(db_index=True)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='posts')
    date_pub = models.DateTimeField(auto_now_add=True)
    is_test = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        return self.text[:20]

    class Meta:
        ordering = ['-date_pub']

    @property
    def date_pub_formatted(self):
        return self.date_pub.strftime('%d.%m.%y')


class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_LENGTH, default=DEFAULT_TAG_NAME)
    telegram_user = models.ForeignKey('TelegramUser', blank=True, null=True,
                                      on_delete=models.CASCADE, related_name='tags')
    is_test = models.BooleanField(blank=True, null=True, default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class TelegramUser(AbstractUser):
    tg_id = models.IntegerField(unique=True, blank=True, null=True)
    tg_username = models.CharField(max_length=200, blank=True, null=True)
    tg_auth_date = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.tg_id} {self.tg_username}"

    @staticmethod
    @sync_to_async
    def make_from_dict(data):
        username = str(data['id'])
        password = DEFAULT_PASSWORD
        user, created = TelegramUser.objects.get_or_create(tg_id=data.get('id', ''),
                                                           username=username, password=password)
        user.tg_username = data.get('username', '')
        user.tg_auth_date = data.get('auth_date', '')
        user.save()
        return user
