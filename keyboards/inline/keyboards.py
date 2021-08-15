from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

item_cb = CallbackData('item', 'action', 'value', 'second_value')

from typing import Union


async def get_list(items: list, action: str, back_value: Union[str, bool] = False) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for item in items:
        markup.insert(
            InlineKeyboardButton(item.name, callback_data=item_cb.new(action=action,
                                                                      value=item.id,
                                                                      second_value=back_value))
        )
    return markup


async def table_menu(table_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('All fields', callback_data=item_cb.new(action='rows_list',
                                                                     value=table_id,
                                                                     second_value=False)),
        InlineKeyboardButton('Add field', callback_data=item_cb.new(action='add_row',
                                                                    value=table_id,
                                                                    second_value=False))
    ).add(
        InlineKeyboardButton('Remove table', callback_data=item_cb.new(action='delete_table',
                                                                       value=table_id,
                                                                       second_value=False))
    ).add(
        InlineKeyboardButton('Back', callback_data=item_cb.new(action='tables_list',
                                                               value=table_id,
                                                               second_value=False))
    )


async def row_menu(row_id: int, table_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('All transactions', callback_data=item_cb.new(action='transactions_list',
                                                                           value=row_id,
                                                                           second_value=table_id)),
        InlineKeyboardButton('Add transaction', callback_data=item_cb.new(action='add_transaction',
                                                                          value=row_id,
                                                                          second_value=table_id)),
    ).add(
        InlineKeyboardButton('Remove row', callback_data=item_cb.new(action='remove_row',
                                                                     value=row_id,
                                                                     second_value=table_id))
    ).add(
        InlineKeyboardButton('Back', callback_data=item_cb.new(action='rows_list',
                                                               value=table_id,
                                                               second_value=table_id))
    )


async def transaction_menu(transaction_id: int, row_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Add transaction', callback_data=item_cb.new(action='add_transaction',
                                                                          value=transaction_id,
                                                                          second_value=row_id))
    ).add(
        InlineKeyboardButton('Back', callback_data=item_cb.new(action='rows_list',
                                                               value=row_id,
                                                               second_value=row_id))
    )


async def transaction_detail_menu(transaction_id: int, row_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Delete', callback_data=item_cb.new(action='delete_transaction',
                                                                 value=transaction_id,
                                                                 second_value=row_id))
    ).add(
        InlineKeyboardButton('Back', callback_data=item_cb.new(action='transactions_list',
                                                               value=row_id))
    )
