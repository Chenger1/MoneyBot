from aiogram import types

from loader import dp

from keyboards.inline import keyboards

from db.models import Transaction


@dp.callback_query_handler(keyboards.item_cb.filter(action='transactions_list'))
async def transactions_list(call: types.CallbackQuery, callback_data: dict):
    row_id = callback_data.get('value')
    instances = await Transaction.filter(row__id=row_id)
    if not instances:
        await call.answer('There are no transactions. Create a new one')
        return
    keyboard = await keyboards.get_list(instances, 'transaction_detail', row_id)
    await call.message.edit_text('Transactions:', reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(keyboards.item_cb.filter(action='transaction_detail'))
async def transaction_detail(call: types.CallbackQuery, callback_data: dict):
    value = callback_data.get('value')
    row_id = callback_data.get('second_value')
    trans = await Transaction.get_or_none(id=value)
    if not trans:
        await call.answer('There is no such transaction. Create a new one')
        return
    trans_type = 'Income' if trans.type else 'Outcome'
    text = f'№{trans.number}\n' + \
           f'Type: <b>{trans_type}</b>' + \
           f'Sum: {trans.amount}' + \
           f'<em>{trans.created}</em>' + \
           f'Category: <strong>{trans.category}</strong>'
    keyboard = await keyboards.transaction_menu(trans.id, row_id)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()
