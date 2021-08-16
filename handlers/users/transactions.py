from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from keyboards.dispatcher import dispatcher
from loader import dp

from keyboards.inline import keyboards
from keyboards.default import keyboards as default_keyboards

from db.models import Transaction, Category, Row, User

from handlers.users.category import list_categories

from states.state_groups import CreateTransaction


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


@dp.message_handler(Text(equals=['Stop']), state=CreateTransaction)
async def stop_transaction(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        keyboard, path = await dispatcher('LEVEL_2_TABLE')
        data.pop('transaction')
        await message.answer('Tables, Rows, Transactions', reply_markup=keyboard)
        data['path'] = path


@dp.callback_query_handler(keyboards.item_cb.filter(action='add_transaction'))
async def add_transaction_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await CreateTransaction.starter.set()
    await call.message.answer('Create Transaction', reply_markup=default_keyboards.stop_create_object_button)
    await call.message.answer('Choose transaction type', reply_markup=keyboards.transaction_type)
    await CreateTransaction.transaction_type.set()
    async with state.proxy() as data:
        data['transaction'] = {
            'row_id': callback_data.get('second_value')
        }
    await call.answer()


@dp.callback_query_handler(keyboards.item_cb.filter(action='transaction_type'), state=CreateTransaction.transaction_type)
async def transaction_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    async with state.proxy() as data:
        data['transaction']['type'] = value
    await call.message.answer('Input sum')
    await CreateTransaction.amount.set()
    await call.answer()


@dp.message_handler(state=CreateTransaction.amount)
async def input_transaction_amount(message: types.Message, state: FSMContext):
    try:
        potential_number = message.text.replace(' ', '')  # remove whitespaces
        async with state.proxy() as data:
            data['transaction']['amount'] = float(potential_number)
        categories = await list_categories(message.from_user.id, 'transaction_category')
        if not categories:
            await message.answer('There are not categories.\n' +
                                 'This field will be set as empty.\n Confirm',
                                 reply_markup=keyboards.confirm_keyboard)
            await CreateTransaction.save.set()
            return
        await message.answer('Choose category', reply_markup=categories)
        await CreateTransaction.category.set()
    except ValueError:
        await message.answer('Given text is not a number')


@dp.callback_query_handler(keyboards.item_cb.filter(action='transaction_category'), state=CreateTransaction.category)
async def transaction_category(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    value = callback_data.get('value')
    async with state.proxy() as data:
        data['transaction']['category_id'] = value
        await call.message.answer('Confirm', reply_markup=keyboards.confirm_keyboard)
        await CreateTransaction.save.set()
    await call.answer()


@dp.callback_query_handler(keyboards.item_cb.filter(action='confirm_action'), state=CreateTransaction.save)
async def save_transaction(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    confirmed = callback_data.get('value')
    if confirmed:
        async with state.proxy() as data:
            number = await Transaction.get_next_number(call.from_user.id)
            category = None
            if data['transaction'].get('category_id'):
                category = await Category.get(id=data['transaction']['category_id'])
            row = await Row.get(id=data['transaction']['row_id'])
            user = await User.get(user_id=call.from_user.id)
            try:
                await Transaction.create(number=number,
                                         type=data['transaction']['type'],
                                         amount=data['transaction']['amount'],
                                         category=category,
                                         row=row, user=user)
                await call.answer('Transaction has been created')
            except Exception as e:
                await call.message.answer(str(e))
            finally:
                await state.finish()
                keyboard, path = await dispatcher('LEVEL_2_TABLE')
                data.pop('transaction')
                await call.message.answer('Tables, Rows, Transactions', reply_markup=keyboard)
                data['path'] = path
    else:
        async with state.proxy() as data:
            await state.finish()
            keyboard, path = await dispatcher('LEVEL_2_TABLE')
            data.pop('transaction')
            await call.message.answer('Canceled', reply_markup=keyboard)
            data['path'] = path
