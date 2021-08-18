from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.dispatcher import FSMContext

from loader import dp

from keyboards.dispatcher import dispatcher, back_button
from keyboards.inline import keyboards

from db.models import User, Utils

from utils import statistic
from utils.get_utils import change_transaction_amount_according_to_currency
from states.state_groups import ChangePercentage, ChangeCurrency


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


@dp.message_handler(Text(equals=['Utils']))
async def get_utils_menu(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_UTILS')
    await message.answer('Utils', reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['Current tax']))
async def get_current_tax_handler(message: types.Message):
    utils = await Utils.load()
    await message.answer(f'<b>Tax: </b> {utils.default_percent}%')


@dp.message_handler(Text(equals=['Current currency']))
async def get_current_currency(message: types.Message):
    utils = await Utils.load()
    await message.answer(f'<b>Current: </b> {utils.default_currency}')


@dp.message_handler(Text(equals=['Change currency']))
async def change_currency(message: types.Message):
    await ChangeCurrency.starter.set()
    await message.answer('Choose new currency', reply_markup=keyboards.currency_keyboard)
    await ChangeCurrency.currency.set()


@dp.callback_query_handler(keyboards.item_cb.filter(action='change_currency'), state=ChangeCurrency.currency)
async def change_currency_callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    utils = await Utils.load()
    if not value == utils.default_currency:
        old_currency = utils.default_currency
        utils.default_currency = value
        await utils.save()
        await call.answer('Currency has been changed')
        data = await state.get_data()
        await state.finish()
        await state.update_data(**data)
        await change_transaction_amount_according_to_currency(call.from_user.id, old_currency)
    else:
        await call.answer('This currency is set already')
        data = await state.get_data()
        await state.finish()
        await state.update_data(**data)


@dp.message_handler(Text(equals=['Change taxes percentage']))
async def change_percentage(message: types.Message):
    await ChangePercentage.starter.set()
    await message.answer('Input new percentage. Be sure to not input a float number, only integer')
    await ChangePercentage.integer.set()


@dp.message_handler(state=ChangePercentage.integer)
async def change_integer_handler(message: types.Message, state: FSMContext):
    number_str = message.text
    try:
        number = int(number_str)
        utils = await Utils.load()
        utils.default_percent = number
        await utils.save()
        await message.answer('New percentage has been saved')
        data = await state.get_data()
        await state.finish()
        await state.update_data(**data)
    except ValueError:
        await message.answer('Wrong format. Try again')
