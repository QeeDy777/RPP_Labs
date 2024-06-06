from aiogram.fsm.state import StatesGroup, State


class AddCurrency(StatesGroup):
    currency_name = State()
    rate = State()


class DeleteCurrency(StatesGroup):
    currency_name = State()


class UpdateCurrency(StatesGroup):
    currency_name = State()
    rate = State()


class ConvertCurrency(StatesGroup):
    currency_name = State()
    amount = State()
