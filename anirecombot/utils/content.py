import pathlib
from json import JSONDecodeError
from logging import getLogger

from aiogram.client.session import aiohttp
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from requests.exceptions import ConnectionError

logger = getLogger(__name__)


async def get_data_from_url(url: str, message: Message, err_msg: str = None):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f'HTTP error: {response.status}')
                    await message.answer(err_msg)
        except (JSONDecodeError, TelegramBadRequest, aiohttp.ClientError, ConnectionError) as e:
            logger.error(f'Exception occurred: {e}')
            await message.answer(err_msg)


async def get_image_extension(url: str) -> str:
    path = pathlib.Path(url)
    image_extension = path.suffix[1:]
    logger.debug(f'Image extension: {image_extension}')

    return image_extension
