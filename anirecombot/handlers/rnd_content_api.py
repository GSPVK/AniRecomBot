import requests
from requests.exceptions import ConnectionError
from json import JSONDecodeError

from aiogram import Router, F
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

router = Router()


@router.message(F.text.casefold() == 'quote')
async def send_quote(message: Message) -> None:
    """
    Get random quote from https://animechan.xyz/
    """
    try:
        data = requests.get('https://animechan.xyz/api/random').json()
    except (JSONDecodeError, TelegramBadRequest, ConnectionError):
        await message.answer(f'I\'m sorry, but i currently unable to fetch a random quote. Please try again later.')
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
    try:
        baka = requests.get('https://nekos.best/api/v2/baka').json()
    except (JSONDecodeError, TelegramBadRequest, ConnectionError):
        await message.answer(
            f'I\'m sorry, but i couldn\'t find any "baka!" gifs at the moment. Please try again later.')
    else:
        url_baka = baka['results'][0]['url']
        await message.answer_animation(url_baka)
