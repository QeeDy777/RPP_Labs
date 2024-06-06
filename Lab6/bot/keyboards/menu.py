from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="manage_currency", description="Управление валютами"),
        BotCommand(command="get_currencies", description="Получить список валют"),
        BotCommand(command="convert", description="Конвертировать валюту")
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
