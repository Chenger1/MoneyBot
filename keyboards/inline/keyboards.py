from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

item_cb = CallbackData('item', 'action', 'value')


async def get_list(items: list, action: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for item in items:
        markup.insert(
            InlineKeyboardButton(item.name, callback_data=item_cb.new(action=action,
                                                                      value=item.id))
        )
    return markup


async def table_menu(table_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('All fields', callback_data=item_cb.new(action='all_transactions',
                                                                     value=table_id))
    ).add(
        InlineKeyboardButton('Add field', callback_data=item_cb.new(action='add_transaction',
                                                                    value=table_id))
    ).add(
        InlineKeyboardButton('Remove table', callback_data=item_cb.new(action='delete_table',
                                                                       value=table_id))
    ).add(
        InlineKeyboardButton('Back', callback_data=item_cb.new(action='list_tables',
                                                               value=table_id))
    )
