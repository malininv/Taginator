from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from asgiref.sync import sync_to_async
import django
from tag_bot.callback_datas import main_callback, tag_callback
from tag_bot.keyboards import main_keyboard, create_choose_tag_keyboard, post_keyboard, context, action
from django.db.models import Count

django.setup()
from tag_web.models import Tag, TelegramUser, Post

API_TOKEN = '6218657645:AAEkL8K5ofbAu0-6fI4gCqmdgn8iQpvdtUk'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class CreateTagState(StatesGroup):
    waiting_for_tag_name = State()


@dp.message_handler(commands=['start'])
async def send_main_keyboard(message: types.Message):
    await message.answer('Choose your tag or create new one.', reply_markup=main_keyboard)
    telegram_user, created = await TelegramUser.objects.aget_or_create(telegram_id=message.from_user.id)
    default_tag, created = await Tag.objects.aget_or_create(name='No tag', telegram_user=telegram_user)


@dp.callback_query_handler(main_callback.filter(type="create", context=context.main))
async def create_tag(call: CallbackQuery, callback_data: dict):
    await call.message.answer("<b>Send me new tag name</b>", parse_mode='HTML')
    await CreateTagState.waiting_for_tag_name.set()


@dp.callback_query_handler(main_callback.filter(type="delete", context=context.main))
async def delete_tag(call: CallbackQuery, callback_data: dict):
    tags = await get_all_tags(call.from_user.id)
    await call.message.edit_reply_markup(
        await create_choose_tag_keyboard(tags, callback_data['context'], action.delete))


@dp.callback_query_handler(main_callback.filter(type="choose", context=context.main))
@dp.callback_query_handler(main_callback.filter(type="choose", context=context.post))
async def choose_tag_from_main(call: CallbackQuery, callback_data: dict):
    tags = await get_all_tags(call.from_user.id)
    keyboard = await create_choose_tag_keyboard(tags, callback_data['context'], action.choose)
    await call.message.edit_text('Choose your tag', reply_markup=keyboard)


@dp.callback_query_handler(main_callback.filter(type="main", context=context.main), )
async def back_to_main(call: CallbackQuery, callback_data: dict):
    await call.message.edit_text('Choose your tag or create new one.', reply_markup=main_keyboard)


@sync_to_async
def get_all_tags(user):
    tags = Tag.objects.filter(telegram_user__telegram_id=user).annotate(count=Count('posts'))
    return tags


@sync_to_async
def get_or_create_tag(name, user_id):
    telegram_user = TelegramUser.objects.get(telegram_id=user_id)
    tag, created = Tag.objects.get_or_create(name=name, telegram_user=telegram_user)
    return tag, created


@dp.message_handler(state=CreateTagState.waiting_for_tag_name)
async def create_tag(message: types.Message, state: FSMContext):
    tag, created = await get_or_create_tag(message.text, message.from_user.id)
    if created:
        await message.answer(f"'{tag.name}' tag created.", reply_markup=main_keyboard)
    else:
        await message.answer(f"'{tag.name}' tag is already there.", reply_markup=main_keyboard)
    await state.finish()


@dp.callback_query_handler(tag_callback.filter(context=context.post, action=action.choose))
async def choose_tag_for_post(call: CallbackQuery, callback_data: dict):
    tag_name = callback_data.get('name')
    tag = await Tag.objects.aget(name=tag_name, telegram_user__telegram_id=call.from_user.id)
    post = await Post.objects.acreate(text=call.message.text, tag=tag)
    await call.message.edit_text(f'Post with tag "{tag_name}" is successfully saved.', reply_markup=main_keyboard)


@dp.callback_query_handler(tag_callback.filter(context=context.main, action=action.choose))
async def choose_tag_for_main(call: CallbackQuery, callback_data: dict):
    tag_name = callback_data.get('name')
    tag = await Tag.objects.aget(name=tag_name, telegram_user__telegram_id=call.from_user.id)
    posts = Post.objects.filter(tag=tag)
    feed = await create_post_feed(posts, tag)
    await call.message.edit_text(feed, parse_mode='HTML', reply_markup=main_keyboard)


@sync_to_async()
def create_post_feed(posts, tag):
    if not posts:
        return 'Oops.. There is no posts..'
    feed = f'🗂 <b>{tag.name}</b>\n\n'
    sep = '_' * 12
    for post in posts:
        feed += f'<b>{post.date_pub_formatted}</b>\n\n{post.text}\n{sep}\n\n'
    return feed


@dp.callback_query_handler(tag_callback.filter(context=context.main, action=action.delete))
async def delete_tag_for_main(call: CallbackQuery, callback_data: dict):
    tag_name = callback_data.get('name')
    tag = await Tag.objects.aget(name=tag_name, telegram_user__telegram_id=call.from_user.id)
    await make_default_tags(tag, call.from_user.id)
    await tag.adelete()
    await call.message.edit_text(f'"{tag_name}" tag is removed.', parse_mode='HTML', reply_markup=main_keyboard)


@sync_to_async()
def make_default_tags(tag, user_id):
    posts = Post.objects.filter(tag=tag)
    default_tag = Tag.objects.get(name='No tag', telegram_user__telegram_id=user_id)
    for post in posts:
        post.tag = default_tag
    Post.objects.bulk_update(posts, ['tag'])
@dp.message_handler()
async def tag_choose(message: types.Message):
    await message.answer(f'{message.text}', reply_markup=post_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
