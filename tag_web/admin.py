from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Tag, Post, TelegramUser


admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(TelegramUser, UserAdmin)
