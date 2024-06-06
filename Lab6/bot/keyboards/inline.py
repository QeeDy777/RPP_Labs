from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

select_mc = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Добавить валюту",
            callback_data="add_currency"
        )
    ],
    [
        InlineKeyboardButton(
            text="Удалить валюту",
            callback_data="delete_currency"
        )
    ],
    [
        InlineKeyboardButton(
            text="Обновить курс валюты",
            callback_data="update_currency"
        )
    ]
])
