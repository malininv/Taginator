import json
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseNotAllowed, JsonResponse
from django.contrib.auth import login
from django.template.loader import render_to_string
from .models import Tag, Post, TelegramUser
from .utils import HashCheck, DEFAULT_THEME
from Taginator import local_settings


@login_required
def index(request):
    user = request.user
    tags = Tag.objects.filter(telegram_user__tg_id=user.tg_id).annotate(count=Count('posts')).order_by('-count')
    search_param = request.GET.get('search', '')
    tag_param = request.GET.get('tags')
    posts = Post.objects.filter(tag__telegram_user__tg_id=user.tg_id)
    if search_param:
        posts = posts.filter(text__icontains=search_param)
    if tag_param:
        posts = posts.filter(tag__name__in=tag_param.split(','))

    theme = request.session.get('theme') or DEFAULT_THEME

    context = {
        'tags': tags,
        'posts': posts,
        'host': request.get_host(),
        'theme': theme,
        'is_checked': theme == 'dark'
    }
    return render(request, 'tag_web/index.html', context=context)


def auth(request):
    secret = local_settings.TELEGRAM_BOT_TOKEN.encode('utf-8')
    if not HashCheck(request.GET, secret).check_hash():
        return render(request, 'tag_web/error.html', {
            'msg': 'Упс.. Что-то пошло не так..'
        })
    user = TelegramUser.objects.get(tg_id=request.GET['id'])
    login(request, user)
    return redirect('/')


def login_telegram(request):
    return render(request, 'tag_web/login.html')


@login_required
def update_session(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest' or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = json.load(request)
    request.session['theme'] = data.get('theme')
    return HttpResponse()


@login_required
def update_content(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest' or not request.method == 'GET':
        return HttpResponseNotAllowed(['GET'])
    user = request.user
    tag_param = request.GET.get('tags')
    search_param = request.GET.get('search')
    posts = Post.objects.filter(tag__telegram_user__tg_id=user.tg_id)
    if tag_param:
        posts = posts.filter(tag__name__in=tag_param.split(','))

    # getting tags to highlight them after searching
    tags = []
    if search_param:
        posts = posts.filter(text__icontains=search_param)
        tags = list(set(posts.values_list('tag__name', flat=True)))

    context = {'posts': posts}
    content = render_to_string('tag_web/content.html', context)
    return JsonResponse({'content': content, 'tags': tags}, safe=False)


@login_required
def create_tag(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest' or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = json.load(request)
    user_id = request.session['user_id']
    tag_name = data.get('tag')

    return HttpResponse()
