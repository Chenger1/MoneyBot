from aiogram.dispatcher.filters.state import  State, StatesGroup


class CreateTable(StatesGroup):
    starter = State()
    name = State()
    field = State()
    save = State()


class CreateRow(StatesGroup):
    starter = State()
    name = State()


class CreateTransaction(StatesGroup):
    starter = State()
    transaction_type = State()
    amount = State()
    category = State()
    save = State()


class CreateCategory(StatesGroup):
    starter = State()
    name = State()
