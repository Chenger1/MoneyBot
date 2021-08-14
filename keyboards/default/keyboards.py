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
