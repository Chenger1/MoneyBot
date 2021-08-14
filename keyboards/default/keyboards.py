from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


level_1_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Tables'),
    KeyboardButton('Categories')
)


level_2_table_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('List tables'),
    KeyboardButton('Create table')
).add(
    KeyboardButton('Back')
)


level_2_category_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('List Categories'),
    KeyboardButton('Create Category')
).add(
    KeyboardButton('Back')
)


stop_create_object_button = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Stop')
)


stop_with_create_buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Save table'),
    KeyboardButton('Stop')
)
