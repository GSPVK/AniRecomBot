import logging

from aiogram import Router, F
from aiogram.types import Message

from anirecombot.utils.content import get_data_from_url

router = Router()

logger = logging.getLogger(__name__)


@router.message(F.text.casefold() == 'quote')
async def send_quote(message: Message) -> None:
    """
    Get random quote from https://animechan.xyz/
    """
    data = await get_data_from_url(
        url='https://animechan.xyz/api/random',
        message=message,
        err_msg=f'I\'m sorry, but i currently unable to fetch a random quote. Please try again later.'
    )
    if data:
        anime = data['anime']
        character = data['character']
        quote = data['quote']
        await message.answer(f'<b>Anime:</b> {anime}\n<b>Character:</b> {character}\n\n<i>{quote}</i>')


@router.message(F.text.casefold() == 'b..baka!')
async def send_baka(message: Message) -> None:
    """
    Get "Baka" from https://nekos.best/api/v2/baka
    """
    data = await get_data_from_url(
        url='https://nekos.best/api/v2/bakas',
        message=message,
        err_msg=f'I\'m sorry, but i couldn\'t find any "baka!" gifs at the moment. Please try again later.'
    )
    if data:
        url_baka = data['results'][0]['url']
        await message.answer_animation(url_baka)
