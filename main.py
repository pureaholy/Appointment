import os

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from dotenv import load_dotenv
import utils.database as db
from handlers import basic, admin, client


async def on_startup(dp):
    await db.db_start()
    basic.setup(dp, bot)
    admin.setup(dp, bot)
    client.setup(dp, bot)


if __name__ == '__main__':
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(LoggingMiddleware())

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
