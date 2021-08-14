from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from loader import dp

from db.models import Table, Transaction, Row, User, get_next_pk

from keyboards.inline import keyboards
from keyboards.dispatcher import dispatcher, back_button
from keyboards.default.keyboards import stop_create_object_button, stop_with_create_buttons

from states.state_groups import CreateTable


@dp.message_handler(Text(equals=['List tables']))
async def list_tables(message: types.Message):
    tables = await Table.filter(user__user_id=message.from_user.id)
    if not tables:
        await message.answer('There are no any tables. Create one')
        return
    keyboard = await keyboards.get_list(tables, 'table_detail')
    await message.answer('Tables:', reply_markup=keyboard)


@dp.message_handler(Text(equals=['Tables']))
async def tables_menu(message: types.Message, state: FSMContext):
    keyboard, path = await dispatcher('LEVEL_2_TABLE')
    await message.answer('Tables menu', reply_markup=keyboard)
    await state.update_data(path=path)


@dp.callback_query_handler(keyboards.item_cb.filter(action='table_list'))
async def list_tables_callback(call: types.CallbackQuery):
    tables = await Table.filter(user__user_id=call.message.from_user.id)
    keyboard = await keyboards.get_list(tables, 'table_detail')
    await call.message.edit_text('Tables:', reply_markup=keyboard)


@dp.callback_query_handler(keyboards.item_cb.filter(action='table_detail'))
async def detail_table(call: types.CallbackQuery, callback_data: dict):
    value = callback_data.get('value')
    table = await Table.get_or_none(id=value)
    if not table:
        await call.answer('There is not such table')
        return
    last_transactions = await Transaction.filter(row__table__id=value)[:3]
    if not last_transactions:
        text = f'There are no any transactions yet'
    else:
        text = ''
        for item in last_transactions:
            text += f'№{item.number}. {item.created}\n In <b>{item.category}</b>. Sum: <b>{item.amount}</b>'
    keyboard = await keyboards.table_menu(value)
    await call.message.edit_text(text, reply_markup=keyboard)


@dp.message_handler(Text(equals=['Stop']), state='*')
async def stop(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        keyboard, path = await back_button(data['path'])
        await state.finish()
        await message.answer('Stopped', reply_markup=keyboard)
        data['path'] = path


@dp.message_handler(Text(equals=['Create table']))
async def create_table(message: types.Message, state: FSMContext):
    await CreateTable.starter.set()
    await message.answer('Add table name', reply_markup=stop_create_object_button)
    await CreateTable.name.set()
    await state.update_data(table={})


@dp.message_handler(state=CreateTable.name)
async def set_table_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['table']['name'] = message.text
        await message.answer('Add fields. Input names. Press "Save table" you don`t want to add more fields',
                             reply_markup=stop_with_create_buttons)
        await CreateTable.field.set()
        data['table']['fields'] = []


@dp.message_handler(Text(equals=['Save table']), state=CreateTable.field)
async def save_table(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = data['table']['name']
        user = await User.get(user_id=message.from_user.id)
        try:
            table = await Table.create(name=name, id=await get_next_pk(Table),
                                       user=user)
        except Exception as e:
            await message.answer(str(e))
        else:
            for item in data['table']['fields']:
                await Row.create(name=item, id=await get_next_pk(Row),
                                 table=table)
            keyboard, path = await back_button(data['path'])
            await state.finish()
            data['path'] = path
            await message.answer('Table created', reply_markup=keyboard)


@dp.message_handler(state=CreateTable.field)
async def add_table_fields(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['table']['fields'].append(message.text)
    await message.answer('This field added')
