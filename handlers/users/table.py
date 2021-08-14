from aiogram import types
from aiogram.dispatcher.filters import Text

from loader import dp

from db.models import Table, Transaction

from keyboards.inline import keyboards


@dp.message_handler(Text(equals=['Tables']))
async def list_tables(message: types.Message):
    tables = await Table.filter(user__user_id=message.from_user.id)
    if not tables:
        await message.answer('There are no any tables. Create one')
        return
    keyboard = await keyboards.get_list(tables, 'table_detail')
    await message.answer('Tables:', reply_markup=keyboard)


@dp.callback_query_handler(keyboards.item_cb.filter(action='table_list'))
async def list_tables_callback(call: types.CallbackQuery):
    tables = await Table.filter(user__user_id=call.message.from_user.id)
    keyboard = await keyboards.get_list(tables, 'table_detail')
    await call.message.edit_text('Tables:', reply_markup=keyboard)


@dp.callback_query_handler(keyboards.item_cb.filter(action='table_detail'))
async def detail_table(call: types.CallbackQuery, callback_data: dict):
    value = callback_data.get('value')
    table = await Table.get_or_none(id=value)
    if not table:
        await call.answer('There is not such table')
        return
    last_transactions = await Transaction.filter(row__table__id=value)
    if not last_transactions:
        text = f'There are no any transactions yet'
    else:
        text = ''
        for item in last_transactions:
            text += f'№{item.number}. {item.created}\n In <b>{item.category}</b>. Sum: <b>{item.amount}</b>'
    keyboard = await keyboards.table_menu(value)
    await call.message.edit_text(text, reply_markup=keyboard)
