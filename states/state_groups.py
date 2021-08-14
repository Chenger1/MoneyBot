from aiogram.dispatcher.filters.state import  State, StatesGroup


class CreateTable(StatesGroup):
    starter = State()
    name = State()
    field = State()
    save = State()


class CreateRow(StatesGroup):
    starter = State()
    name = State()
    save = State()


class Transaction(StatesGroup):
    starter = State()
    transaction_type = State()
    amount = State()
    category = State()
    save = State()
