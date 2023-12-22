import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis

from anirecombot.data.config_reader import config
from anirecombot.handlers import setup_routers


async def main():
    """
    Start the polling process.
    """
    token = config.bot_token.get_secret_value()
    bot = Bot(token=token, parse_mode='HTML')
    redis = aioredis.Redis(host=config.redis_host,
                           port=config.redis_port,
                           username=config.redis_user or None,
                           password=config.redis_password.get_secret_value() or None)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(bot=bot, storage=storage)
    router = setup_routers()
    dp.include_routers(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, redis=redis)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
