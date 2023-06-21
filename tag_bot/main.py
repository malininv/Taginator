import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from asgiref.sync import sync_to_async
import django
from tag_bot.callback_datas import main_callback, tag_callback
from tag_bot.keyboards import main_keyboard, create_choose_tag_keyboard, post_keyboard, context, action, create_keyboard
from django.db.models import Count

django.setup()
from tag_web.models import Tag, TelegramUser, Post, DEFAULT_TAG_NAME
from tag_web.utils import TestData, delete_test_data
from Taginator.local_settings import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

MAX_TAG_LENGH = 50
MAIN_KEYBOARD_MSG = 'Отправьте сообщение чтобы сохранить.\n\nДля просмотра существующих сообщение выберите тег.'


class CreateTagState(StatesGroup):
    waiting_for_tag_name = State()


@dp.message_handler(commands=['start'])
async def send_main_keyboard(message: types.Message):
    await message.answer(MAIN_KEYBOARD_MSG, reply_markup=main_keyboard)
    telegram_user, created = await TelegramUser.objects.aget_or_create(tg_id=message.from_user.id)
    default_tag, created = await Tag.objects.aget_or_create(name=DEFAULT_TAG_NAME, telegram_user=telegram_user)


@dp.callback_query_handler(main_callback.filter(type="create", context=context.main))
async def create_tag(call: CallbackQuery, callback_data: dict):
    await call.message.edit_text("<b>Отправьте мне новый тег </b>", parse_mode='HTML', reply_markup=create_keyboard)
    await CreateTagState.waiting_for_tag_name.set()


@dp.callback_query_handler(main_callback.filter(type="create_test", context=context.main))
async def delete_test_data_main(call: CallbackQuery, callback_data: dict):
    await call.message.edit_text('Идет сбор данных, пожалуйста, подождите.')
    test_data = TestData(call.from_user.id)
    await test_data.create_random_data()
    await call.message.edit_text('Данные готовы. Нажмите "Выбрать" для просмотра доступных категорий.',
                                 reply_markup=main_keyboard)


@dp.callback_query_handler(main_callback.filter(type="delete_test", context=context.main))
async def delete_test_data_main(call: CallbackQuery, callback_data: dict):
    await delete_test_data(call.from_user.id)
    await call.message.edit_text('Тестовые данные успешно удалены.', reply_markup=main_keyboard)


@dp.callback_query_handler(main_callback.filter(type="delete", context=context.main))
async def delete_tag(call: CallbackQuery, callback_data: dict):
    tags = await get_all_tags(call.from_user.id)
    keyboard = await create_choose_tag_keyboard(tags, callback_data['context'], action.delete)
    await call.message.edit_text('Выберите тег для удаления.\n\n<b>Связанным с тегом посты будет удалены.</b>',
                                 reply_markup=keyboard, parse_mode='HTML')


@dp.callback_query_handler(main_callback.filter(type="choose", context=context.main))
async def choose_tag_from_main(call: CallbackQuery, callback_data: dict):
    tags = await get_all_tags(call.from_user.id)
    keyboard = await create_choose_tag_keyboard(tags, callback_data['context'], action.choose)
    await call.message.edit_text('Выберите тег', reply_markup=keyboard)


@dp.callback_query_handler(main_callback.filter(type="choose", context=context.post))
async def choose_tag_from_post(call: CallbackQuery, callback_data: dict):
    tags = await get_all_tags(call.from_user.id)
    keyboard = await create_choose_tag_keyboard(tags, callback_data['context'], action.choose)
    await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(main_callback.filter(type="main", context=context.main))
async def back_to_main_from_main(call: CallbackQuery, callback_data: dict):
    await call.message.edit_text(MAIN_KEYBOARD_MSG, reply_markup=main_keyboard)


@dp.callback_query_handler(main_callback.filter(type="main", context=context.main),
                           state=CreateTagState.waiting_for_tag_name)
async def back_to_main_from_main(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()
    await call.message.edit_text(MAIN_KEYBOARD_MSG, reply_markup=main_keyboard)


@dp.callback_query_handler(main_callback.filter(type="main", context=context.post))
async def back_to_main_from_post(call: CallbackQuery, callback_data: dict):
    await call.message.edit_reply_markup(reply_markup=post_keyboard)


@sync_to_async
def get_all_tags(user):
    tags = Tag.objects.filter(telegram_user__tg_id=user).annotate(count=Count('posts')).order_by('-count')
    return tags


@sync_to_async
def get_or_create_tag(name, user_id):
    user = TelegramUser.objects.get(tg_id=user_id)
    tag, created = Tag.objects.get_or_create(name=name, telegram_user=user)
    return tag, created


@dp.message_handler(state=CreateTagState.waiting_for_tag_name)
async def create_tag(message: types.Message, state: FSMContext):
    if len(message.text) > MAX_TAG_LENGH:
        await message.answer(f"Тег слишком длинный. Максимальная длинна {MAX_TAG_LENGH} символа.",
                             reply_markup=main_keyboard)
        await state.finish()
        return
    tag, created = await get_or_create_tag(message.text, message.from_user.id)
    if created:
        await message.answer(f"'{tag.name}' тег успешно создан.", reply_markup=main_keyboard)
    else:
        await message.answer(f"'{tag.name}' тег уже существует", reply_markup=main_keyboard)
    await state.finish()


@dp.callback_query_handler(tag_callback.filter(context=context.post, action=action.choose))
async def choose_tag_for_post(call: CallbackQuery, callback_data: dict):
    tag_name = callback_data.get('name')
    tag = await Tag.objects.aget(name=tag_name, telegram_user__tg_id=call.from_user.id)
    post = await Post.objects.acreate(text=call.message.text, tag=tag)
    await call.message.edit_text(f'Пост с тегом "{tag_name}" успешно сохранен', reply_markup=main_keyboard)


@dp.callback_query_handler(tag_callback.filter(context=context.main, action=action.choose))
async def choose_tag_for_main(call: CallbackQuery, callback_data: dict):
    tag_name = callback_data.get('name')
    tag = await Tag.objects.aget(name=tag_name, telegram_user__tg_id=call.from_user.id)
    posts = Post.objects.filter(tag=tag)
    feed = await create_post_feed(posts, tag)
    await call.message.edit_text(feed, reply_markup=main_keyboard, disable_web_page_preview=True)


@sync_to_async()
def create_post_feed(posts, tag):
    if not posts:
        return 'Упс.. С таким тегом постов не существует...'
    feed = f'🗂 {tag.name}\n\n'
    sep = '_' * 12 + '\n\n'
    post_count = posts.count()
    for index, post in enumerate(posts, start=1):
        if index == post_count:
            sep = ''
        feed += f'{post.date_pub_formatted}\n\n{post.text}\n{sep}'
    return feed


@dp.callback_query_handler(tag_callback.filter(context=context.main, action=action.delete))
async def delete_tag_for_main(call: CallbackQuery, callback_data: dict):
    tag_name = callback_data.get('name')
    tag = await Tag.objects.aget(name=tag_name, telegram_user__tg_id=call.from_user.id)
    await tag.adelete()
    await call.message.edit_text(f'Тег "{tag_name}" успешно удален.', parse_mode='HTML', reply_markup=main_keyboard)


@dp.message_handler()
async def tag_choose(message: types.Message):
    await message.answer(f'{message.text}', reply_markup=post_keyboard, disable_web_page_preview=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
