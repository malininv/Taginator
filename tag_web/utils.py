import hashlib
import hmac
import random
import django
import requests
import json

django.setup()
from tag_web.models import Tag, Post, TelegramUser

DEFAULT_THEME = 'dark'


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
    def __init__(self, user_id):
        self.user_id = user_id
        self.genres = [(1, 'Анекдот'),
                       (2, 'Рассказы'),
                       (3, 'Стишки'),
                       (4, 'Афоризмы'),
                       (5, 'Цитаты'),
                       (6, 'Тосты'),
                       (8, 'Статусы'),
                       (11, 'Анекдот (+18)'),
                       (12, 'Рассказы (+18)'),
                       (13, 'Стишки (+18)'),
                       (14, 'Афоризмы (+18)'),
                       (15, 'Цитаты (+18)'),
                       (16, 'Тосты (+18)'),
                       (18, 'Статусы (+18)')]

        self.tag_amount = random.randint(5, 10)
        self.post_amount = random.randint(1, 12)
        self.random_genres = random.sample(self.genres, k=self.tag_amount)

    async def create_random_data(self):
        user = await TelegramUser.objects.aget(tg_id=self.user_id)
        for index, name in self.random_genres:
            tag = await Tag.objects.acreate(name=name, telegram_user=user)
            post_amount = random.randint(1, 12)
            for _ in range(post_amount + 1):
                anecdot = await self._get_random_anecdot(index)
                if anecdot is not None:
                    await Post.objects.acreate(text=anecdot, tag=tag)

    async def _get_random_anecdot(self, index):
        anecdot = requests.get(f'http://rzhunemogu.ru/RandJSON.aspx?CType={index}')
        try:
            anecdot = anecdot.json(strict=False)
            anecdot = anecdot.get('content')
        except:
            return
        return anecdot
