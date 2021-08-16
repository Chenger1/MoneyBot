from aiogram import types

from loader import dp

from keyboards.inline import keyboards
from keyboards.inline.keyboards import item_cb

from db.models import Category, Transaction, Row, Table


@dp.callback_query_handler(item_cb.filter(action='filter_transaction'))
async def filter_transaction(call: types.CallbackQuery, callback_data: dict):
    all_categories = await Category.filter(user__user_id=call.from_user.id)
    categories_keyboard = await keyboards.get_list(all_categories, 'filter_by_category')
    await call.message.answer('Choose filter type', reply_markup=categories_keyboard)
    await call.answer()


@dp.callback_query_handler(item_cb.filter(action='filter_by_category'))
async def filter_by_category(call: types.CallbackQuery, callback_data: dict):
    value = callback_data.get('value')
    transactions = await Transaction.filter(category__id=value)
    if not transactions:
        await call.answer('There are no such transactions with this category')
        return
    row = await Row.get(id=transactions[0].row_id)
    table = await Table.get(id=row.table_id)
    keyboard = await keyboards.get_list(transactions, 'transaction_detail', str(row.id))
    keyboard.row(
        types.InlineKeyboardButton('Back', callback_data=keyboards.item_cb.new(action='table_statistic',
                                                                               value=table.id,
                                                                               second_value=False))
    )
    await call.message.answer('Transactions by category:', reply_markup=keyboard)
    await call.answer()
