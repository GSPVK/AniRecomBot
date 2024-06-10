import logging
from json import JSONDecodeError

from aiogram import Router, F
from aiogram.client.session import aiohttp
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from requests.exceptions import ConnectionError

router = Router()

logger = logging.getLogger(__name__)


@router.message(F.text.casefold() == 'quote')
async def send_quote(message: Message) -> None:
    """
    Get random quote from https://animechan.xyz/
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'https://animechan.xyz/api/random') as response:
                data = await response.json()
        except (JSONDecodeError, TelegramBadRequest, aiohttp.ClientError, ConnectionError) as e:
            await message.answer(f'I\'m sorry, but i currently unable to fetch a random quote. Please try again later.')
            logger.error(e)
        else:
            anime = data['anime']
            character = data['character']
            quote = data['quote']
            await message.answer(f'<b>Anime:</b> {anime}\n<b>Character:</b> {character}\n\n<i>{quote}</i>')


@router.message(F.text.casefold() == 'b..baka!')
async def send_baka(message: Message) -> None:
    """
    Get "Baka" from https://nekos.best/api/v2/baka
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'https://nekos.best/api/v2/baka') as response:
                data = await response.json()
        except (JSONDecodeError, TelegramBadRequest, aiohttp.ClientError, ConnectionError) as e:
            await message.answer(
                f'I\'m sorry, but i couldn\'t find any "baka!" gifs at the moment. Please try again later.')
            logger.error(e)
        else:
            url_baka = data['results'][0]['url']
            await message.answer_animation(url_baka)
