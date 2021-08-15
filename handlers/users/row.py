from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline import keyboards

from loader import dp

from db.models import Row, Transaction, Table

from states.state_groups import CreateRow
from tortoise.exceptions import IntegrityError, ValidationError


async def rows_list(table_id: Union[str, int]):
    rows = await Row.filter(table__id=table_id)
    if not rows:
        return None
    keyboard = await keyboards.get_list(rows, 'row_detail', table_id)
    keyboard.row(
        types.InlineKeyboardButton('Back', callback_data=keyboards.item_cb.new(action='table_detail',
                                                                               value=table_id,
                                                                               second_value=False))
    )
    return keyboard


@dp.callback_query_handler(keyboards.item_cb.filter(action='rows_list'))
async def row_list(call: types.CallbackQuery, callback_data: dict):
    rows = await rows_list(callback_data.get('value'))
    if not rows:
        await call.answer('There are no fields yet. Create new one')
        return

    await call.message.edit_text('Rows:', reply_markup=rows)
    await call.answer()


@dp.callback_query_handler(keyboards.item_cb.filter(action='row_detail'))
async def row_detail(call: types.CallbackQuery, callback_data: dict):
    row_id = callback_data.get('value')
    table_id = callback_data.get('second_value')
    row = await Row.get_or_none(id=row_id)
    if not row:
        await call.answer('There is no such row')
    last_transactions = await Transaction.filter(row__id=row_id)
    if not last_transactions:
        text = 'There are no transactions yet'
    else:
        text = ''
        for item in last_transactions:
            text += f'№{item.number}. {item.created}\n In <b>{item.category}</b>. Sum: <b>{item.amount}</b>'
    keyboard = await keyboards.row_menu(row.id, table_id)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(keyboards.item_cb.filter(action='delete_row'))
async def delete_row(call: types.CallbackQuery, callback_data: dict):
    value = callback_data.get('value')
    table_id = callback_data.get('second_value')
    row = await Row.get_or_none(id=value)
    if not row:
        await call.answer('There is no such row')
        return
    await row.delete()
    rows = await rows_list(table_id)
    if not rows:
        await call.message.edit_text('There are no any rows. Create a new one', rows)
        return
    await call.message.edit_text('Rows:', reply_markup=rows)
    await call.answer('Row has been deleted')


@dp.callback_query_handler(keyboards.item_cb.filter(action='add_row'))
async def add_row(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await CreateRow.starter.set()
    table_id = callback_data.get('value')
    await call.message.answer('Add field name')
    await CreateRow.name.set()
    async with state.proxy() as data:
        data['row'] = {}
        data['row']['table'] = table_id
    await call.answer()


@dp.message_handler(state=CreateRow.name)
async def add_row_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            table = await Table.get(id=data['row']['table'])
            row = await Row.create(name=message.text, table=table)
        except (ValidationError, IntegrityError) as e:
            await message.answer(str(e))
        else:
            await state.finish()
            data.pop('row')
            await message.answer('Row created')
            await rows_list(table.id)
