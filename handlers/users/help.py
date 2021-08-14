from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Commands list: ",
            "/start - Start",
            "/help - Get help")
    
    await message.answer("\n".join(text))
