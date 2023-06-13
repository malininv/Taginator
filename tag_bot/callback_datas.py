from aiogram.utils.callback_data import CallbackData

main_callback = CallbackData("manage", "type", "context")

post_callback = CallbackData("post", "context")

tag_callback = CallbackData("tag", "name", "context", "action")