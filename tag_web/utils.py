import hashlib
import hmac
import random
import django
import requests
from asgiref.sync import sync_to_async
from django.http import HttpResponseNotAllowed
django.setup()
from tag_web.models import Tag, Post, TelegramUser

DEFAULT_THEME = 'light'


class HashCheck:
    def __init__(self, data, secret):
        self.hash = data.get('hash', '')
        self.secret_key = hashlib.sha256(secret).digest()
        self.data = {}
        for k, v in data.items():
            if k != 'hash':
                self.data[k] = v

    def data_check_string(self):
        a = sorted(self.data.items())
        res = '\n'.join(map(lambda x: '='.join(x), a))
        return res

    def calc_hash(self):
        msg = bytearray(self.data_check_string(), 'utf-8')
        res = hmac.new(self.secret_key, msg=msg, digestmod=hashlib.sha256).hexdigest()
        return res

    def check_hash(self):
        return self.calc_hash() == self.hash


class TestData:
    genres = [(1, 'Анекдот'),
              (2, 'Рассказы'),
              (3, 'Стишки'),
              (4, 'Афоризмы'),
              (5, 'Цитаты'),
              (6, 'Тосты'),
              (8, 'Статусы')]

    def __init__(self, user_id):
        self.user_id = user_id
        self.tag_amount = random.randint(4, 7)
        self.post_amount = random.randint(3, 10)
        self.random_genres = random.sample(self.genres, k=self.tag_amount)

    @sync_to_async
    def create_random_data(self):
        user = TelegramUser.objects.get(tg_id=self.user_id)
        for index, name in self.random_genres:
            tag, created = Tag.objects.get_or_create(name=name, telegram_user=user, is_test=True)
            posts = []
            for _ in range(self.post_amount + 1):
                anecdot = self._get_random_anecdot(index)
                if anecdot is not None:
                    posts.append(Post(text=anecdot, tag=tag, is_test=True).clean_fields())
            Post.objects.bulk_create(posts)

    def _get_random_anecdot(self, index):
        anecdot = requests.get(f'http://rzhunemogu.ru/RandJSON.aspx?CType={index}')
        try:
            anecdot = anecdot.json(strict=False)
            anecdot = anecdot.get('content')
        except:
            return
        return anecdot



@sync_to_async
def delete_test_data(user_id):
    Tag.objects.filter(is_test=True, telegram_user__tg_id=user_id).delete()


def is_ajax(request, method: str):
    if method == 'GET':
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest' or not request.method == 'GET':
            return HttpResponseNotAllowed(['GET'])
    if method == 'POST':
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest' or not request.method == 'POST':
            return HttpResponseNotAllowed(['POST'])


