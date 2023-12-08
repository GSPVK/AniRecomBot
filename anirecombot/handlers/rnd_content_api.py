import requests
from json import JSONDecodeError
from random import choice
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.exceptions import TelegramBadRequest

from requests.exceptions import ConnectionError

router = Router()


@router.message(Text('Quote'))
async def send_quote(message: Message):
    """
    Get random quote from https://animechan.xyz/
    """
    try:
        data = requests.get('https://animechan.xyz/api/random').json()
    except (JSONDecodeError, TelegramBadRequest, ConnectionError):
        await message.answer(f'I\'m sorry, but I\'m currently unable to fetch a random quote. Please try again later.')
    else:
        anime = data['anime']
        character = data['character']
        quote = data['quote']
        await message.answer(f'<b>Anime:</b> {anime}\n<b>Character:</b> {character}\n\n<i>{quote}</i>')


@router.message(Text('PicRandom'))
async def random_image(message: Message):
    """
    Get random image from https://waifu.pics/docs

    In the "categories" list, you can add any categories available
    on waifu.pics, and the randomizer will choose a random one from them.
    """
    categories = ['awoo', 'waifu', 'neko']
    category = choice(categories)

    try:
        pic = requests.get(f'https://api.waifu.pics/sfw/{category}').json()
    except (JSONDecodeError, TelegramBadRequest, ConnectionError):
        await message.answer(f'I\'m sorry, but I\'m currently unable to fetch a PicRandom. Please try again later.')
    else:
        url_pic = pic['url']
        await message.answer_photo(url_pic)


@router.message(Text('B..Baka!'))
async def send_baka(message: Message):
    """
    Get "Baka" from https://catboys.com/api/
    """
    try:
        baka = requests.get('https://api.catboys.com/baka').json()
    except (JSONDecodeError, TelegramBadRequest, ConnectionError):
        await message.answer(
            f'I\'m sorry, but I\'m I couldn\'t find any "baka!" gifs at the moment. Please try again later.')
    else:
        url_baka = baka['url']
        await message.answer_animation(url_baka)
