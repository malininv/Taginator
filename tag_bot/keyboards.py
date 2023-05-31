from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from tag_bot.callback_datas import main_callback, tag_callback


@sync_to_async
def create_choose_tag_keyboard(tags):
    buttons = []
    for tag in tags:
        buttons.append([InlineKeyboardButton(text=f"{tag.name}", callback_data=tag_callback.new(name=f"{tag.name}"))])
    buttons.append([back_to_main])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


main_keyboard_buttons = [
    [InlineKeyboardButton(text="Choose tag", callback_data=main_callback.new(type="choose")),
     InlineKeyboardButton(text="Create tag", callback_data=main_callback.new(type="create"))]
]
back_to_main = InlineKeyboardButton(text="Back to main", callback_data=main_callback.new(type="main"))
main_keyboard = InlineKeyboardMarkup(inline_keyboard=main_keyboard_buttons)
