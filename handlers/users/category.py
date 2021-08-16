from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from loader import dp


from keyboards.inline import keyboards as inline_keyboards
from keyboards.dispatcher import dispatcher

from db.models import Category

from typing import Optional


async def list_categories(user_id: int) -> Optional[types.InlineKeyboardMarkup]:
    instances = await Category.filter(user__pk=user_id)
    if not instances:
        return None
    keyboard = await inline_keyboards.get_list(instances, 'category_detail')
    return keyboard


@dp.message_handler(Text(equals=['Categories']))
async def categories_menu(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_CATEGORY')
    await message.answer('Categories menu', reply_markup=keyboard)
    await state.update_data(path=path)


@dp.message_handler(Text(equals=['List Categories']))
async def list_category_handler(message: types.Message):
    keyboard = await list_categories(message.from_user.id)
    if not keyboard:
        await message.answer('There are no categories. Create a new one')
        return
    await message.answer('Categories:', reply_markup=keyboard)


@dp.message_handler(Text(equals=['Create category']))
async def create_category_handler(message: types.Message, state: FSMContext):
    pass
