import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from anirecombot.config_reader import config
from anirecombot.handlers import setup_routers


async def main():
    """
    Start the polling process.
    """
    token = config.bot_token.get_secret_value()
    bot = Bot(token=token, parse_mode='HTML')
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)
    router = setup_routers()
    dp.include_routers(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
