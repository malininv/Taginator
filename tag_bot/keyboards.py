from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from collections import namedtuple
from tag_bot.callback_datas import main_callback, tag_callback

Context = namedtuple('Context', ['main', 'post'])
context = Context('main', 'post')

Action = namedtuple('Action', ['choose', 'delete'])
action = Action('choose', 'delete')


@sync_to_async
def create_choose_tag_keyboard(tags, context, action):
    keyboard = InlineKeyboardMarkup(row_width=2)
    back_to_main = InlineKeyboardButton(text="Back",
                                        callback_data=main_callback.new(type="main", context=context))
    if tags:
        for tag in tags:
            if (action == 'delete' or context == 'post') and tag.name == 'No tag':
                continue
            callback_data = tag_callback.new(name=f"{tag.name}", context=context, action=action)
            keyboard.insert(
                InlineKeyboardButton(text=f"{tag.name} ({tag.count})", callback_data=callback_data))
        keyboard.insert(back_to_main)
        return keyboard
    keyboard.insert(back_to_main)
    return keyboard


main_keyboard_buttons = [
    [InlineKeyboardButton(text="📚 Choose tag", callback_data=main_callback.new(type="choose", context=context.main)),
     InlineKeyboardButton(text="➕ Create tag", callback_data=main_callback.new(type="create", context=context.main)),
     InlineKeyboardButton(text="🗑 Delete tag", callback_data=main_callback.new(type="delete", context=context.main))],
    [InlineKeyboardButton(text="🌐 Open website", callback_data=main_callback.new(type="website", context=context.main),
                          url='http://127.0.0.1:8000/admin/')]
]

main_keyboard = InlineKeyboardMarkup(inline_keyboard=main_keyboard_buttons)

post_keyboard_buttons = [
    [InlineKeyboardButton(text="📚 Choose tag", callback_data=main_callback.new(type="choose", context=context.post)),
     InlineKeyboardButton(text="🤷‍♂️ No tag", callback_data=tag_callback.new(name="No tag", context=context.post,
                                                                        action=action.choose)),
    InlineKeyboardButton(text="Cancel", callback_data=main_callback.new(type="main", context=context.main))
     ]
]

post_keyboard = InlineKeyboardMarkup(inline_keyboard=post_keyboard_buttons)
