from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from loader import dp

from db.models import Table, Transaction, Row, User, get_next_pk, Category, Tax

from keyboards.inline import keyboards
from keyboards.dispatcher import dispatcher, back_button
from keyboards.default.keyboards import stop_create_object_button, stop_with_create_buttons

from states.state_groups import CreateTable
from tortoise.functions import Sum, Avg
from tortoise.query_utils import Q


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


@dp.callback_query_handler(keyboards.item_cb.filter(action='tables_list'))
async def list_tables_callback(call: types.CallbackQuery):
    tables = await Table.filter(user__user_id=call.from_user.id)
    keyboard = await keyboards.get_list(tables, 'table_detail')
    await call.message.edit_text('Tables:', reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(keyboards.item_cb.filter(action='table_detail'))
async def detail_table(call: types.CallbackQuery, callback_data: dict):
    value = callback_data.get('value')
    table = await Table.get_or_none(id=value)
    if not table:
        await call.answer('There is not such table')
        return
    last_transactions = await Transaction.filter(row__table__id=value)
    if not last_transactions:
        text = f'There are no any transactions yet'
    else:
        text = ''
        for item in last_transactions[:5]:
            created = item.created.strftime('%Y-%m-%d')
            category = 'Without category'
            if item.category_id:
                category = await Category.get(id=item.category_id)
                category = category.name
            text += f'№{item.number} from {created}\nIn <b>{category}</b>. Sum: <b>{item.amount}</b>\n' + \
                    '---------------\n'
    keyboard = await keyboards.table_menu(value)
    await call.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(keyboards.item_cb.filter(action='delete_table'))
async def delete_table(call: types.CallbackQuery, callback_data: dict):
    value = callback_data.get('value')
    table = await Table.get_or_none(id=value)
    if not table:
        await call.answer('There is no such table')
        return
    await table.delete()
    await call.answer('Table has been deleted')
    tables = await Table.filter(user__user_id=call.from_user.id)
    if not tables:
        await call.message.answer('There are no any tables. Create one')
        return
    keyboard = await keyboards.get_list(tables, 'table_detail')
    await call.message.edit_text('Tables:', reply_markup=keyboard)


@dp.message_handler(Text(equals=['Stop']), state='*')
async def stop(message: types.Message, state: FSMContext):
    keywords = ('table', 'row', 'transaction')
    async with state.proxy() as data:
        keyboard, path = await back_button(data['path'])
        await state.finish()
        await message.answer('Stopped', reply_markup=keyboard)
        data['path'] = path
        for key in keywords:
            if data.get(key):
                data.pop(key)


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
            data.pop('table')
            data['path'] = path
            await message.answer('Table created', reply_markup=keyboard)


@dp.message_handler(state=CreateTable.field)
async def add_table_fields(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['table']['fields'].append(message.text)
    await message.answer('This field added')


@dp.callback_query_handler(keyboards.item_cb.filter(action='table_statistic'))
async def table_statistic(call: types.CallbackQuery, callback_data: dict):
    table_id = callback_data.get('value')
    table = await Table.get(id=table_id)
    incomes_list = await Transaction.annotate(total_sum=Sum('amount')).filter(row__table=table, type=True).\
        values('total_sum')
    outcomes_list = await Transaction.annotate(total_sum=Sum('amount')).filter(row__table=table, type=False). \
        values('total_sum')
    rows_ids = await Row.filter(table=table).values_list('id', flat=True)
    average_incomes_list = await Transaction.all().\
        annotate(avg=Avg('amount', _filter=Q(row_id__in=rows_ids, type=True))).values('avg')
    average_outcomes_list = await Transaction.all(). \
        annotate(avg=Avg('amount', _filter=Q(row_id__in=rows_ids, type=False))).values('avg')
    incomes, outcomes = 0, 0
    average_income = round((average_incomes_list[0].get('avg') or 0), 2)
    average_outcome = round((average_outcomes_list[0].get('avg') or 0), 2)
    for item in incomes_list:
        incomes += item['total_sum']
    for item in outcomes_list:
        outcomes += item['total_sum']
    balance = incomes - outcomes
    text = f'<b>{table.name}</b>\n' + \
           f'Incomes: {incomes}. Outcomes: {outcomes}\n' + \
           f'Average income: {average_income}.\nAverage outcome: {average_outcome}\n' + \
           f'Balance: {balance}'
    await call.message.edit_text(text, reply_markup=await keyboards.table_statistic_keyboard(table_id))


@dp.callback_query_handler(keyboards.item_cb.filter(action='taxes_list'))
async def taxes_list_handler(call: types.CallbackQuery, callback_data: dict):
    table_id = callback_data.get('value')
    taxes = await Tax.filter(transaction__row__table__id=table_id)
    if not taxes:
        await call.answer('There are no taxes yet. Add transaction first')
        return
    text = ''
    for index, item in enumerate(taxes, start=1):
        await item.fetch_related('transaction')
        text += f'{index}. №{item.transaction.number}\n' + \
                f'<b>Transaction sum:</b> {item.transaction.amount}\n' + \
                f'<b>Tax:</b> {item.percent}%\n' + \
                f'<b>Sum to pay:</b> {item.sum}\n\n'
    keyboard = await keyboards.back_keyboard(table_id, 'table_detail')
    await call.message.edit_text(text, reply_markup=keyboard)
