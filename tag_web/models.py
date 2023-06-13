from django.db import models


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
        return self.date_pub.strftime('%c')


class Tag(models.Model):
    name = models.CharField(max_length=50, default='No tag')
    telegram_user = models.ForeignKey('TelegramUser', blank=True, on_delete=models.CASCADE, related_name='tags')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name) + f' ({self.telegram_user})'


class TelegramUser(models.Model):
    telegram_id = models.IntegerField(unique=True, blank=True)

    def __str__(self):
        return str(self.telegram_id)

