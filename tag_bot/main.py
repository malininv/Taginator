from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import BotCommand, BotCommandScopeChat, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from asgiref.sync import sync_to_async
from aiogram.utils.exceptions import BadRequest
import django
from tag_bot.callback_datas import main_callback, tag_callback
from tag_bot.keyboards import main_keyboard, create_choose_tag_keyboard

django.setup()
from tag_web.models import Tag

API_TOKEN = '6218657645:AAEkL8K5ofbAu0-6fI4gCqmdgn8iQpvdtUk'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class CreateTagState(StatesGroup):
    waiting_for_tag_name = State()



@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Hey!\nI can store your messages with tags. It helps to navigate through them.\n"
                         "There is also very handy web site to make navigation even better!",
                         reply_markup=main_keyboard)


@dp.callback_query_handler(main_callback.filter(type="create"))
async def create_tag(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    await call.message.answer("Enter tag name:")
    await CreateTagState.waiting_for_tag_name.set()


@dp.callback_query_handler(main_callback.filter(type="choose"))
async def choose_tag(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    tags = await get_all_tags()
    await call.message.edit_reply_markup(await create_choose_tag_keyboard(tags))


@dp.callback_query_handler(main_callback.filter(type="main"))
async def back_to_main(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    await call.message.edit_reply_markup(main_keyboard)


@sync_to_async
def get_all_tags():
    return Tag.objects.all()


@sync_to_async
def get_or_create_tag(name):
    return Tag.objects.get_or_create(name=name)


@sync_to_async
def save_tag(tag):
    tag.save()


@dp.message_handler(state=CreateTagState.waiting_for_tag_name)
async def create_tag(message: types.Message, state: FSMContext):
    tag_object = await get_or_create_tag(message.text)
    tag, is_created = tag_object[0], tag_object[1]
    if is_created:
        await save_tag(tag)
        await message.answer(f"'{tag.name}' created.", reply_markup=main_keyboard)
    else:
        await message.answer(f"'{tag.name}' is already there.", reply_markup=main_keyboard)
    await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
