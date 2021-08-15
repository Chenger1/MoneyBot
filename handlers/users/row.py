from aiogram import types

from keyboards.inline import keyboards

from loader import dp

from db.models import Row, Transaction


@dp.callback_query_handler(keyboards.item_cb.filter(action='rows_list'))
async def row_list(call: types.CallbackQuery, callback_data: dict):
    table_id = callback_data.get('value')
    rows = await Row.filter(table__id=table_id)
    if not rows:
        await call.answer('There are no rows yet. Create new one')
        return
    keyboard = await keyboards.get_list(rows, 'row_detail', table_id)
    keyboard.row(
        types.InlineKeyboardButton('Back', callback_data=keyboards.item_cb.new(action='table_detail',
                                                                               value=table_id,
                                                                               second_value=False))
    )
    await call.message.edit_text('Rows:', reply_markup=keyboard)
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
