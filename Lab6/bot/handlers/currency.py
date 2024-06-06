from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import requests
from aiogram.filters import Command

from bot.keyboards.inline import select_mc
from bot.db.cur import conn
from bot.states.states import AddCurrency, DeleteCurrency, UpdateCurrency, ConvertCurrency

router = Router()


@router.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Я бот для управления валютами. Используйте команды /manage_currency, "
                         "/get_currencies и /convert.")


@router.message(Command("manage_currency"))
async def manage_currency_command(message: Message):
    await message.answer("Выберите действие:", reply_markup=select_mc)


@router.message(Command("get_currencies"))
async def get_currencies_callback(message: Message):
    try:
        response = requests.get("http://localhost:5002/get_currencies")
        response.raise_for_status()
        data = response.json()
        currencies = data["currencies"]

        if currencies:
            currency_list = "\n".join(f"{currency[0]}: {currency[1]}" for currency in currencies)
            await message.answer(f"Список валют:\n{currency_list}")
        else:
            await message.answer("Список валют пуст.")

    except requests.exceptions.RequestException as e:
        await message.answer(f"Ошибка при получении списка валют: {e}")


@router.callback_query(F.data == "add_currency")
async def add_currency_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название валюты:")
    await state.set_state(AddCurrency.currency_name)


@router.message(AddCurrency.currency_name)
async def process_currency_name(message: Message, state: FSMContext):
    currency_name = message.text

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
        if cur.fetchone() is not None:
            await message.answer("Данная валюта уже существует.")
            await state.clear()
            return

    await state.update_data(currency_name=currency_name)
    await message.answer("Введите курс к рублю:")
    await state.set_state(AddCurrency.rate)


@router.message(AddCurrency.rate)
async def process_rate(message: Message, state: FSMContext):
    rate = message.text

    try:
        rate = float(rate)
    except ValueError:
        await message.answer("Неверный формат курса. Введите число.")
        return

    data = await state.get_data()
    currency_name = data["currency_name"]

    try:
        response = requests.post("http://localhost:5001/add_currency",
                                 json={"currency_name": currency_name, "rate": rate})
        response.raise_for_status()
        await message.answer(f"Валюта: {currency_name} успешно добавлена")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при добавлении валюты: {e}")  # Вывод ошибки в терминал
        await message.answer("Произошла ошибка при добавлении валюты. Попробуйте еще раз позже.")
    finally:
        await state.clear()


@router.callback_query(F.data == "delete_currency")
async def delete_currency_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название валюты:")
    await state.set_state(DeleteCurrency.currency_name)


@router.message(DeleteCurrency.currency_name)
async def process_delete_currency(message: Message, state: FSMContext):
    currency_name = message.text

    try:
        response = requests.post("http://localhost:5001/delete_currency", json={"currency_name": currency_name})
        response.raise_for_status()
        await message.answer(f"Валюта: {currency_name} успешно удалена")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при удалении валюты: {e}")  # Вывод ошибки в терминал
        await message.answer("Произошла ошибка при удалении валюты. Попробуйте еще раз позже.")
    finally:
        await state.clear()


@router.callback_query(F.data == "update_currency")
async def update_currency_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название валюты:")
    await state.set_state(UpdateCurrency.currency_name)


@router.message(UpdateCurrency.currency_name)
async def process_update_currency_name(message: Message, state: FSMContext):
    currency_name = message.text

    await state.update_data(currency_name=currency_name)
    await message.answer("Введите курс к рублю:")
    await state.set_state(UpdateCurrency.rate)


@router.message(UpdateCurrency.rate)
async def process_update_rate(message: Message, state: FSMContext):
    rate = message.text

    try:
        rate = float(rate)
    except ValueError:
        await message.answer("Неверный формат курса. Введите число.")
        return

    data = await state.get_data()
    currency_name = data["currency_name"]

    try:
        response = requests.post("http://localhost:5001/update_currency",
                                 json={"currency_name": currency_name, "rate": rate})
        response.raise_for_status()
        await message.answer(f"Курс валюты {currency_name} успешно обновлен")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обновлении курса валюты: {e}")  # Вывод ошибки в терминал
        await message.answer("Произошла ошибка при обновлении курса валюты. Попробуйте еще раз позже.")
    finally:
        await state.clear()


@router.message(Command("convert"))
async def convert_currency_command(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertCurrency.currency_name)


@router.message(ConvertCurrency.currency_name)
async def process_convert_currency_name(message: Message, state: FSMContext):
    currency_name = message.text

    await state.update_data(currency_name=currency_name)
    await message.answer("Введите сумму:")
    await state.set_state(ConvertCurrency.amount)


@router.message(ConvertCurrency.amount)
async def process_convert_amount(message: Message, state: FSMContext):
    amount = message.text

    try:
        amount = float(amount)
    except ValueError:
        await message.answer("Неверный формат суммы. Введите число.")
        return

    data = await state.get_data()
    currency_name = data["currency_name"]

    try:
        response = requests.get(f"http://localhost:5002/convert_currency?currency_name={currency_name}&amount={amount}")
        response.raise_for_status()
        result = response.json()
        converted_amount = result["converted_amount"]
        await message.answer(f"Сумма {amount} {currency_name} равна {converted_amount} рублям")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при конвертации валюты: {e}")  # Вывод ошибки в терминал
        await message.answer("Произошла ошибка при конвертации валюты. Попробуйте еще раз позже.")
    finally:
        await state.clear()
