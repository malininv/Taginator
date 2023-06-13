from django.contrib import admin
from .models import Tag, Post, TelegramUser


admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(TelegramUser)
