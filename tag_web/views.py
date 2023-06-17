from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from .models import Tag, Post, TelegramUser
from .utils import HashCheck
from Taginator import local_settings
import pprint


def index(request):
    try:
        user_id = int(request.session['user_id'])
        user = TelegramUser.objects.get(tg_id=user_id)
    except:
        return render(request, "tag_web/login.html", {})

    tags = Tag.objects.filter(telegram_user__tg_id=user_id).annotate(count=Count('posts')).order_by('-count')
    search = request.GET.get('search', '')
    tag = request.GET.get('tag')
    posts = Post.objects.filter(tag__telegram_user__tg_id=user_id)
    print(posts)
    context = {
        'tags': tags,
        'posts': posts,
        'host': request.get_host()
    }

    return render(request, 'tag_web/index.html', context=context)


def auth(request):
    secret = local_settings.TELEGRAM_BOT_TOKEN.encode('utf-8')
    if not HashCheck(request.GET, secret).check_hash():
        return render(request, 'tag_web/error.html', {
            'msg': 'Упс.. Что-то пошло не так..'
        })
    user = TelegramUser.make_from_dict(request.GET)
    request.session['user_id'] = user.tg_id
    return redirect('/')


def logout(request):
    del request.session['user_id']
    return redirect('/')
