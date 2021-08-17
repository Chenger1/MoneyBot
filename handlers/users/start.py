from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.dispatcher import FSMContext

from loader import dp

from keyboards.dispatcher import dispatcher, back_button
from db.models import User

from db.models import Transaction, User

from tortoise.functions import Sum, Avg
from tortoise.query_utils import Q


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


@dp.message_handler(Text(equals=['Statistic'], ignore_case=True))
async def main_statistic(message: types.Message):
    user = await User.get(user_id=message.from_user.id)
    total_incomes = await Transaction.all().annotate(total_sum=Sum('amount', _filter=Q(user=user,
                                                                                       type=True))).\
        values('total_sum')
    total_outcomes = await Transaction.all().annotate(total_sum=Sum('amount', _filter=Q(user=user,
                                                                                        type=False))). \
        values('total_sum')
    average_income_list = await Transaction.all().annotate(avg=Avg('amount', _filter=Q(user=user,
                                                                                       type=False))). \
        values('avg')
    average_outcome_list = await Transaction.all().annotate(avg=Avg('amount', _filter=Q(user=user,
                                                                                        type=False))). \
        values('avg')
    incomes = (total_incomes[0].get('total_sum') or 0) if total_incomes else 0
    outcomes = (total_outcomes[0].get('total_sum') or 0) if total_outcomes else 0
    average_income = round(average_income_list[0].get('avg') or 0) if average_income_list else 0
    average_outcome = round(average_outcome_list[0].get('avg') or 0) if average_outcome_list else 0
    balance = incomes - outcomes
    text = f'<b>Total income:</b> {incomes}\n' + \
           f'<b>Total outcome:</b> {outcomes}\n' + \
           f'<b>Average income:</b> {average_income}\n' + \
           f'<b>Average outcome:</b> {average_outcome}\n' + \
           f'<b>Total balance: </b> {balance}'
    await message.answer(text)
