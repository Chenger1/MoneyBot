from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from loader import dp

from states.state_groups import CreateCategory

from keyboards.default import keyboards
from keyboards.inline import keyboards as inline_keyboards
from keyboards.dispatcher import dispatcher

from db.models import Category, User

from typing import Optional


async def list_categories(user_id: int, action='category_detail') -> Optional[types.InlineKeyboardMarkup]:
    instances = await Category.filter(user__user_id=user_id)
    if not instances:
        return None
    keyboard = await inline_keyboards.get_list(instances, action)
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


@dp.message_handler(Text(equals=['Stop']), state=CreateCategory)
async def category_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await state.finish()
        keyboard, path = await dispatcher('LEVEL_2_CATEGORY')
        data['path'] = path
    await message.answer('Creating category has been canceled', reply_markup=keyboard)


@dp.message_handler(Text(equals=['Create Category']))
async def create_category_handler(message: types.Message):
    await CreateCategory.starter.set()
    await message.answer('Add category name', reply_markup=keyboards.stop_create_object_button)
    await CreateCategory.name.set()


@dp.message_handler(state=CreateCategory.name)
async def set_category_name(message: types.Message, state: FSMContext):
    user = await User.get(user_id=message.from_user.id)
    await Category.create(name=message.text, user=user)
    async with state.proxy() as data:
        await state.finish()
        keyboard, path = await dispatcher('LEVEL_2_CATEGORY')
        data['path'] = path
    await message.answer('Category has been created', reply_markup=keyboard)
