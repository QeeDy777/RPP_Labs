from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
import logging
import os
import psycopg2


logging.basicConfig(level=logging.INFO)
load_dotenv('t.env')
# Установка переменной окружения API_TOKEN
API_TOKEN = os.getenv('API_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Подключение к базе данных
conn = psycopg2.connect(
    host="localhost",
    database="lab5",
    user="qeedy",
    password="postgres"
)

# Создание таблиц в базе данных
with conn.cursor() as cur:
    cur.execute(
        "CREATE TABLE IF NOT EXISTS currencies ("
        "id SERIAL PRIMARY KEY,"
        "currency_name VARCHAR(50) NOT NULL,"
        "rate NUMERIC(50) NOT NULL)"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS admins ("
        "id SERIAL PRIMARY KEY,"
        "chat_id VARCHAR(50) NOT NULL)"
    )
    conn.commit()


def is_admin(user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM admins WHERE chat_id = %s", (str(user_id),))
        result = cur.fetchone()
    return result is not None


class CurrencyState(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_rate = State()
    waiting_for_delete_currency_name = State()
    waiting_for_update_currency_name = State()
    waiting_for_update_rate = State()


@dp.message_handler(commands=['manage_currency'])
async def manage_currency(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("Нет доступа к команде")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Добавить валюту", "Удалить валюту", "Изменить курс валюты")
    await message.reply("Выберите действие:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Добавить валюту")
async def add_currency(message: types.Message):
    await message.reply("Введите название валюты:")
    await CurrencyState.waiting_for_currency_name.set()


@dp.message_handler(state=CurrencyState.waiting_for_currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
        if cur.fetchone() is not None:
            await message.reply("Данная валюта уже существует")
            await state.finish()
        else:
            await state.update_data(currency_name=currency_name)
            await message.reply("Введите курс к рублю:")
            await CurrencyState.waiting_for_rate.set()


@dp.message_handler(state=CurrencyState.waiting_for_rate)
async def process_rate(message: types.Message, state: FSMContext):
    rate = message.text
    data = await state.get_data()
    currency_name = data.get('currency_name')
    with conn.cursor() as cur:
        cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (currency_name, rate))
        conn.commit()
    await message.reply(f"Валюта: {currency_name} успешно добавлена")
    await state.finish()


@dp.message_handler(lambda message: message.text == "Удалить валюту")
async def delete_currency(message: types.Message):
    await message.reply("Введите название валюты:")
    await CurrencyState.waiting_for_delete_currency_name.set()


@dp.message_handler(state=CurrencyState.waiting_for_delete_currency_name)
async def process_delete_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text
    with conn.cursor() as cur:
        cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
        conn.commit()
    await message.reply(f"Валюта: {currency_name} успешно удалена")
    await state.finish()


@dp.message_handler(lambda message: message.text == "Изменить курс валюты")
async def update_currency(message: types.Message):
    await message.reply("Введите название валюты:")
    await CurrencyState.waiting_for_update_currency_name.set()


@dp.message_handler(state=CurrencyState.waiting_for_update_currency_name)
async def process_update_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text
    await state.update_data(currency_name=currency_name)
    await message.reply("Введите новый курс к рублю:")
    await CurrencyState.waiting_for_update_rate.set()


@dp.message_handler(state=CurrencyState.waiting_for_update_rate)
async def process_update_rate(message: types.Message, state: FSMContext):
    rate = message.text
    data = await state.get_data()
    currency_name = data.get('currency_name')
    with conn.cursor() as cur:
        cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (rate, currency_name))
        conn.commit()
    await message.reply(f"Курс валюты {currency_name} успешно обновлен")
    await state.finish()


@dp.message_handler(commands=['get_currencies'])
async def get_currencies(message: types.Message):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM currencies")
        currencies = cur.fetchall()
    if len(currencies) == 0:
        await message.reply("Валюты не найдены")
    else:
        currencies_str = "\n".join([f"{currency[1]}: {currency[2]}" for currency in currencies])
        await message.reply(f"Валюты:\n{currencies_str}")


class ConvertState(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_amount = State()


@dp.message_handler(commands=['convert'])
async def convert(message: types.Message):
    await message.reply("Введите название валюты:")
    await ConvertState.waiting_for_currency_name.set()


@dp.message_handler(state=ConvertState.waiting_for_currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text
    await state.update_data(currency_name=currency_name)
    await message.reply("Введите сумму:")
    await ConvertState.waiting_for_amount.set()


@dp.message_handler(state=ConvertState.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    amount = message.text
    data = await state.get_data()
    currency_name = data.get('currency_name')
    with conn.cursor() as cur:
        cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
        rate = cur.fetchone()
    if rate is None:
        await message.reply("Валюта не найдена")
    else:
        result = float(amount) * float(rate[0])
        await message.reply(f"{amount} {currency_name} = {result:.2f} рублей")
    await state.finish()


async def set_commands(user_id):
    if is_admin(user_id):
        commands = [
            types.BotCommand(command="/start", description="Начало работы"),
            types.BotCommand(command="/manage_currency", description="Управление валютами"),
            types.BotCommand(command="/get_currencies", description="Получить список валют"),
            types.BotCommand(command="/convert", description="Конвертировать валюту")
        ]
    else:
        commands = [
            types.BotCommand(command="/start", description="Начало работы"),
            types.BotCommand(command="/get_currencies", description="Получить список валют"),
            types.BotCommand(command="/convert", description="Конвертировать валюту")
        ]
    await bot.set_my_commands(commands)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await set_commands(message.from_user.id)
    await message.reply("Добро пожаловать! Выберите команду из меню.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    dp.middleware.setup(LoggingMiddleware())
    executor.start_polling(dp, skip_updates=True)