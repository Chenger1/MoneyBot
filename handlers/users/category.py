from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from loader import dp

from states.state_groups import CreateCategory

from keyboards.default import keyboards
from keyboards.inline import keyboards as inline_keyboards
from keyboards.dispatcher import dispatcher

from db.models import Category, User, Transaction

from typing import Optional
from tortoise.functions import Sum


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


@dp.callback_query_handler(inline_keyboards.item_cb.filter(action='categories_list'))
async def list_category_callback(call: types.CallbackQuery, callback_data: dict):
    keyboard = await list_categories(call.from_user.id)
    if not keyboard:
        await call.message.answer('There are no categories. Create a new one')
        return
    await call.message.edit_text('Categories:', reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(inline_keyboards.item_cb.filter(action='delete_category'))
async def delete_category(call: types.CallbackQuery, callback_data: dict):
    instance = await Category.get_or_none(id=callback_data.get('value'))
    if not instance:
        await call.answer('There is no such category')
        return
    await instance.delete()
    await call.answer('Category has been deleted')
    keyboard = await list_categories(call.from_user.id)
    if not keyboard:
        await call.message.answer('There are no categories. Create a new one')
        return
    await call.message.edit_text('Categories:', reply_markup=keyboard)


@dp.callback_query_handler(inline_keyboards.item_cb.filter(action='category_detail'))
async def category_detail(call: types.CallbackQuery, callback_data: dict):
    category_id = callback_data.get('value')
    category = await Category.get_or_none(id=category_id)
    if not category:
        await call.answer('There is no such category')
        return
    await call.answer()
    incomes_list = await Transaction.annotate(total_sum=Sum('amount')).filter(category_id=category_id, type=True).\
        values('total_sum')
    outcomes_list = await Transaction.annotate(total_sum=Sum('amount')).filter(category_id=category_id, type=False).\
        values('total_sum')
    incomes = incomes_list[0].get('total_sum') or 0
    outcomes = outcomes_list[0].get('total_sum') or 0
    balance = incomes - outcomes
    text = f'<b>{category.name}</b>\n' + \
           f'Incomes: {incomes}. Outcomes: {outcomes}\n' + \
           f'Balance: {balance}'
    await call.message.edit_text(text, reply_markup=await inline_keyboards.category_detail_menu(category_id))


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
    data = await state.get_data()
    await state.finish()
    keyboard, path = await dispatcher('LEVEL_2_CATEGORY')
    data['path'] = path
    await state.update_data(**data)
    await message.answer('Category has been created', reply_markup=keyboard)
