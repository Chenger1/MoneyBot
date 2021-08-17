from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.dispatcher import FSMContext

from loader import dp

from keyboards.dispatcher import dispatcher, back_button
from db.models import User

from db.models import Transaction, User

from tortoise.functions import Sum, Avg
from tortoise.query_utils import Q

from utils import statistic


@dp.message_handler(Text(equals=['Back']))
async def back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not data.get('path'):
            await message.answer('No prev. level found. Returned to main menu')
            keyboard, path = await dispatcher('LEVEL_1')
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


@dp.message_handler(Text(equals=['Statistic'], ignore_case=True))
async def main_statistic(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_STATISTIC')
    data = await statistic.get_total_statistic(message.from_user.id)
    text = await statistic.process_statistic(data)

    await message.answer(text, reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Last 7 days']))
async def last_7_days_statistic_handler(message: types.Message):
    data = await statistic.get_last_7_days(message.from_user.id)
    text = await statistic.process_statistic(data)
    await message.answer(text)


@dp.message_handler(Text(equals=['This month']))
async def this_month_statistic_handler(message: types.Message):
    data = await statistic.month_statistic(message.from_user.id)
    text = await statistic.process_statistic(data)
    await message.answer(text)


@dp.message_handler(Text(equals=['Last month']))
async def last_month_statistic_handler(message: types.Message):
    data = await statistic.month_statistic(message.from_user.id, last_month=True)
    text = await statistic.process_statistic(data)
    await message.answer(text)


@dp.message_handler(Text(equals=['This year']))
async def last_month_statistic_handler(message: types.Message):
    data = await statistic.year_statistic(message.from_user.id)
    text = await statistic.process_statistic(data)
    await message.answer(text)


@dp.message_handler(Text(equals=['Last year']))
async def last_month_statistic_handler(message: types.Message):
    data = await statistic.year_statistic(message.from_user.id, last_year=True)
    text = await statistic.process_statistic(data)
    await message.answer(text)
