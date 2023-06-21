import hashlib
import hmac
import random
import django
import requests

from asgiref.sync import sync_to_async
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
    genres = [(1, 'Анекдот'),
              (2, 'Рассказы'),
              (3, 'Стишки'),
              (4, 'Афоризмы'),
              (5, 'Цитаты'),
              (6, 'Тосты'),
              (8, 'Статусы')]

    def __init__(self, user_id):
        self.user_id = user_id
        self.tag_amount = random.randint(5, 7)
        self.post_amount = random.randint(1, 6)
        self.random_genres = random.sample(self.genres, k=self.tag_amount)

    @sync_to_async
    def create_random_data(self):
        user = TelegramUser.objects.get(tg_id=self.user_id)
        tags_already_created = Tag.objects.filter(telegram_user=user).values_list('name', flat=True)
        genres_to_create = [(index, genre) for index, genre in self.random_genres if genre not in tags_already_created]
        objects = self._create_objects(genres_to_create, user)
        tags = [tag for tag, post in objects]
        posts = [post for tag, post in objects]
        posts_lat = [post for sublist in posts for post in sublist]
        Tag.objects.bulk_create(tags)
        Post.objects.bulk_create(posts_lat)

    def _create_objects(self, genres, user):
        objects = []
        for index, tag_name in genres:
            tag_to_create = Tag(name=tag_name, telegram_user=user, is_test=True)
            posts_to_create = self._create_random_posts(index, self.post_amount, tag_to_create)
            objects.append((tag_to_create, posts_to_create))
        return objects

    def _create_random_posts(self, index, amount, tag):
        posts = []
        for _ in range(amount+1):
            anecdot = requests.get(f'http://rzhunemogu.ru/RandJSON.aspx?CType={index}')
            try:
                anecdot = anecdot.json(strict=False)
                anecdot = anecdot.get('content')
            except:
                continue
            posts.append(Post(text=anecdot, tag=tag, is_test=True))
        return posts


@sync_to_async
def delete_test_data(user_id):
    Tag.objects.filter(is_test=True, telegram_user__tg_id=user_id).delete()
