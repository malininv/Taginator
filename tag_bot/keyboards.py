from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LoginUrl, ReplyKeyboardMarkup
from asgiref.sync import sync_to_async
from collections import namedtuple
from tag_bot.callback_datas import main_callback, tag_callback
import django
from django.urls import reverse
django.setup()
from tag_web.models import DEFAULT_TAG_NAME
from Taginator.settings import CURRENT_HOST

AUTH_URL = 'https://' + CURRENT_HOST + reverse('tag_web:auth')
Context = namedtuple('Context', ['main', 'post'])
context = Context('main', 'post')

Action = namedtuple('Action', ['choose', 'delete'])
action = Action('choose', 'delete')


@sync_to_async
def create_choose_tag_keyboard(tags, context, action):
    keyboard = InlineKeyboardMarkup(row_width=2)
    back_to_main = InlineKeyboardButton(text="Назад",
                                        callback_data=main_callback.new(type="main", context=context))
    if tags:
        for tag in tags:
            if action == 'delete' and tag.name == DEFAULT_TAG_NAME:
                continue
            callback_data = tag_callback.new(name=f"{tag.name}", context=context, action=action)
            keyboard.insert(
                InlineKeyboardButton(text=f"{tag.name} ({tag.count})", callback_data=callback_data))
        keyboard.insert(back_to_main)
        return keyboard
    keyboard.insert(back_to_main)
    return keyboard


login_url = LoginUrl(url=AUTH_URL, request_write_access=True,
                     bot_username='taginator_help_bot')
main_keyboard_buttons = [
    [InlineKeyboardButton(text="📚 Выбрать", callback_data=main_callback.new(type="choose", context=context.main)),
     InlineKeyboardButton(text="➕ Создать", callback_data=main_callback.new(type="create", context=context.main)),
     InlineKeyboardButton(text="🗑 Удалить", callback_data=main_callback.new(type="delete", context=context.main))],
    [InlineKeyboardButton(text="🌐 Открыть сайт", login_url=login_url)],
    [InlineKeyboardButton(text="😄 Создать тестовые данные", callback_data=main_callback.new(type="create_test", context=context.main))],
    [InlineKeyboardButton(text="🧹 Очистить тестовые данные",
                          callback_data=main_callback.new(type="delete_test", context=context.main))],
]
cancel_button = InlineKeyboardButton(text="Отмена", callback_data=main_callback.new(type="main", context=context.main))

main_keyboard = InlineKeyboardMarkup(inline_keyboard=main_keyboard_buttons)

post_keyboard_buttons = [
    [InlineKeyboardButton(text="📚 Выбрать тег", callback_data=main_callback.new(type="choose", context=context.post)),
     cancel_button
     ]
]

post_keyboard = InlineKeyboardMarkup(inline_keyboard=post_keyboard_buttons)

create_keyboard = InlineKeyboardMarkup()
create_keyboard.insert(cancel_button)
