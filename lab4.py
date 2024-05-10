from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import logging
import os

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('API_TOKEN')

print(API_TOKEN)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

currency_rates = {}


class Form(StatesGroup):
    name = State()
    currency_name = State()
    currency_rate = State()
    convert_currency_name = State()
    convert_amount = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Я бот для конвертации валют. Как тебя зовут?")
    await Form.name.set()
    print(currency_rates)


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    await message.reply("Привет, " + name + ". Используй команды /save_currency и /convert.")
    await state.finish()


@dp.message_handler(commands=['save_currency'])
async def save_currency(message: types.Message):
    await message.reply("Введите название валюты:")
    await Form.currency_name.set()


@dp.message_handler(state=Form.currency_name)
async def currency_name_handler(message: types.Message, state: FSMContext):
    currency_name = message.text
    await state.update_data(currency_name=currency_name)
    await message.reply(f"Введите курс {currency_name} к рублю:")
    await Form.currency_rate.set()


@dp.message_handler(state=Form.currency_rate)
async def currency_rate_handler(message: types.Message, state: FSMContext):
    try:
        currency_rate = float(message.text.replace(',', '.'))  # Заменяем запятую на точку, чтобы
        # правильно преобразовать в дробное число
        currency_data = await state.get_data()
        currency_name = currency_data['currency_name']
        currency_rates[currency_name] = currency_rate
        await message.reply(f"Курс {currency_name} сохранен: {currency_rate} рублей.")
        await state.finish()
    except ValueError:
        await message.reply("Неверный формат курса валюты. Введите число.")


@dp.message_handler(commands=['convert'])
async def convert_currency(message: types.Message):
    if not currency_rates:
        await message.reply("Нет доступных валют для конвертации.")
    else:
        currency_list = "\n".join(currency_rates.keys())
        await message.reply(f"Доступные валюты:\n{currency_list}\n\nВведите название валюты для конвертации:")
    await Form.convert_currency_name.set()


@dp.message_handler(state=Form.convert_currency_name)
async def convert_currency_name_handler(message: types.Message, state: FSMContext):
    currency_name = message.text
    if currency_name in currency_rates:
        await state.update_data(currency_name=currency_name)
        currency_rate = currency_rates[currency_name]
        await message.reply(f"Курс {currency_name} к рублю: {currency_rate}\nВведите сумму в {currency_name}:")
        await Form.convert_amount.set()
    else:
        await message.reply("Неверное название валюты.")
        await state.finish()


@dp.message_handler(state=Form.convert_amount)
async def convert_amount_handler(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        currency_data = await state.get_data()
        currency_name = currency_data['currency_name']
        rate = currency_rates[currency_name]
        result = amount * rate
        await message.reply(f"{amount} {currency_name} = {result} рублей.")
        await state.finish()
    except ValueError:
        await message.reply("Неверный формат суммы. Введите число.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    dp.middleware.setup(LoggingMiddleware())
    executor.start_polling(dp, skip_updates=True)
