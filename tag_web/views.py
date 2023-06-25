import json
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, HttpResponse
from django.http import  JsonResponse
from django.contrib.auth import login
from django.template.loader import render_to_string
from .models import Tag, Post, TelegramUser
from .forms import FormCreateTag, FormCreatePost
from .utils import HashCheck, DEFAULT_THEME, is_ajax
from Taginator import local_settings


@login_required
def index(request):
    tg_id = request.user.tg_id
    tags = Tag.objects.filter(telegram_user__tg_id=tg_id).annotate(count=Count('posts')).order_by('-count')
    search_param = request.GET.get('search', '')
    tag_param = request.GET.get('tags')
    posts = Post.objects.filter(tag__telegram_user__tg_id=tg_id)
    if search_param:
        posts = posts.filter(text__icontains=search_param)
    if tag_param:
        posts = posts.filter(tag__name__in=tag_param.split(','))

    form_create_tag = FormCreateTag()
    form_create_post = FormCreatePost(tg_id=tg_id)

    theme = request.session.get('theme') or DEFAULT_THEME

    context = {
        'tags': tags,
        'posts': posts,
        'host': request.get_host(),
        'theme': theme,
        'is_checked': theme == 'dark',
        'form_create_tag': form_create_tag,
        'form_create_post': form_create_post
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


# redirect if user is not logged in
def login_telegram(request):
    return render(request, 'tag_web/login.html')


@login_required
def update_session(request):
    is_ajax(request, 'POST')
    data = json.load(request)
    request.session['theme'] = data.get('theme')
    return HttpResponse()


@login_required
def update_content(request):
    is_ajax(request, 'GET')
    user = request.user
    tag_param = request.GET.get('tags')
    search_param = request.GET.get('search')
    posts = Post.objects.filter(tag__telegram_user__tg_id=user.tg_id)
    if tag_param:
        posts = posts.filter(tag__name__in=tag_param.split(','))

    # getting tags to highlight after searching
    tags = []
    if search_param:
        posts = posts.filter(text__icontains=search_param)
        tags = list(set(posts.values_list('tag__name', flat=True)))

    context = {'posts': posts}
    content = render_to_string('tag_web/content.html', context)
    return JsonResponse({'content': content, 'tags': tags}, safe=False)


@login_required
def create_tag(request):
    if request.method != 'POST':
        return redirect('/')
    form = FormCreateTag(request.POST)
    if form.is_valid():
        tag = form.save(commit=False)
        tag.telegram_user = TelegramUser.objects.get(tg_id=request.user.tg_id)
        tag.save()
    return redirect('/')


@login_required
def create_post(request):
    if request.method != 'POST':
        return redirect('/')
    form = FormCreatePost(request.POST, tg_id=request.user.tg_id)
    if form.is_valid():
        form.save()
    return redirect('/')

