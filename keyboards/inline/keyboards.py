from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from typing import Union


item_cb = CallbackData('item', 'action', 'value', 'second_value')


transaction_type = InlineKeyboardMarkup().add(
    InlineKeyboardButton('Income', callback_data=item_cb.new(action='transaction_type',
                                                             value=1,
                                                             second_value=False)),
    InlineKeyboardButton('Outcome', callback_data=item_cb.new(action='transaction_type',
                                                              value=0,
                                                              second_value=False))
)

confirm_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton('Confirm', callback_data=item_cb.new(action='confirm_action',
                                                              value=True,
                                                              second_value=False))
    ).add(InlineKeyboardButton('Do not confirm', callback_data=item_cb.new(action='confirm_action',
                                                                           value=False,
                                                                           second_value=False))
          )


async def get_list(items: list, action: str, back_value: Union[str, bool] = False) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for item in items:
        if hasattr(item, 'name'):
            name = item.name
        else:
            name = item.number
        markup.insert(
            InlineKeyboardButton(name, callback_data=item_cb.new(action=action,
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
        InlineKeyboardButton('Statistic', callback_data=item_cb.new(action='table_statistic',
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
        InlineKeyboardButton('Remove row', callback_data=item_cb.new(action='delete_row',
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
                                                               value=row_id,
                                                               second_value=False))
    )


async def category_detail_menu(category_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Delete', callback_data=item_cb.new(action='delete_category',
                                                                 value=category_id,
                                                                 second_value=False))
    ).add(
        InlineKeyboardButton('Back', callback_data=item_cb.new(action='categories_list',
                                                               value=False,
                                                               second_value=False))
    )


async def table_statistic_keyboard(table_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Filter by category', callback_data=item_cb.new(action='filter_transaction_by_category',
                                                                             value=table_id,
                                                                             second_value=False)),
        InlineKeyboardButton('Filter by type', callback_data=item_cb.new(action='filter_transaction_by_type',
                                                                         value=table_id,
                                                                         second_value=False))
    ).add(
        InlineKeyboardButton('Get SpreadSheet', callback_data=item_cb.new(action='get_spreadsheet',
                                                                          value=table_id,
                                                                          second_value=False))
    ).add(
        InlineKeyboardButton('Back', callback_data=item_cb.new(action='table_detail',
                                                               value=table_id,
                                                               second_value=False))
    )


async def transaction_type_filter(table_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Income', callback_data=item_cb.new(action='filter_by_type',
                                                                 value='1',
                                                                 second_value=table_id)),
        InlineKeyboardButton('Outcome', callback_data=item_cb.new(action='filter_by_type',
                                                                  value='0',
                                                                  second_value=table_id))
    )
