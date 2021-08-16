from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.dispatcher import FSMContext

from loader import dp

from keyboards.dispatcher import dispatcher, back_button
from db.models import User


@dp.message_handler(Text(equals=['Back']))
async def back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not data.get('path'):
            await message.answer('No prev. level found. Returned to main menu')
            keyboard, path = await back_button('LEVEL_1')
        else:
            keyboard, path = await back_button(data['path'])
        await message.answer('Prev level', reply_markup=keyboard)
        data['path'] = path


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    user, created = await User.get_or_create(user_id=message.from_user.id)

    keyboard, path = await dispatcher('LEVEL_1')
    await message.answer(f"Hello, {message.from_user.full_name}!", reply_markup=keyboard)
    await state.update_data(path=path)
    if created:
        await message.answer('Welcome')
    else:
        await message.answer('It`s good to see you again')
