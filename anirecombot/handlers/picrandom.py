import os
import requests
from requests.exceptions import ConnectionError
from json import JSONDecodeError
from random import choice

from aiogram import Router, F, html
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from anirecombot.keyboards import picrandom_kb
from anirecombot.states.picrandom import PicrandomState

router = Router()

categories = {
    'sfw': ['waifu', 'neko', 'shinobu', 'megumin', 'bully', 'cuddle', 'cry', 'hug', 'awoo', 'kiss', 'lick', 'pat',
            'smug', 'bonk', 'yeet', 'blush', 'smile', 'wave', 'highfive', 'handhold', 'nom', 'bite', 'glomp', 'slap',
            'kill', 'kick', 'happy', 'wink', 'poke', 'dance', 'cringe'],
    'nsfw': ['waifu', 'neko', 'trap', 'blowjob']
}


async def get_image_extension(url: str) -> str:
    file_path = url.rsplit('/', 1)[-1]
    image_name, image_extension = os.path.splitext(file_path)
    return image_extension[1:]


async def get_pict(message: Message, category: str, tag: list) -> None:
    """
    Get random image from https://waifu.pics/ (read https://waifu.pics/docs/)
    """
    random_tag = choice(tag)
    try:
        image = requests.get(f'https://api.waifu.pics/{category}/{random_tag}').json()
    except (JSONDecodeError, TelegramBadRequest, ConnectionError):
        await message.answer(f'I\'m sorry, but I\'m currently unable to fetch a PicRandom. Please try again later.')
    else:
        image_url = image['url']
        extension = await get_image_extension(image_url)
        if extension == 'gif':
            await message.answer_animation(
                image_url, caption=f'{html.bold("Category")}: {category}, {html.bold("tag")}: {random_tag}')
        else:
            await message.answer_photo(
                image_url, caption=f'{html.bold("Category")}: {category}, {html.bold("tag")}: {random_tag}')


@router.message(F.text.casefold() == 'back to categories')
async def back_to_categories(message: Message, state: FSMContext) -> None:
    await message.answer(text=f'Category selection', reply_markup=picrandom_kb.select_category)
    await state.clear()
    await state.set_state(PicrandomState.choose_category)


@router.message(F.text.casefold() == 'picrandom')
async def random_image(message: Message, state: FSMContext) -> None:
    await message.answer(text=f'Category selection', reply_markup=picrandom_kb.select_category)
    await state.set_state(PicrandomState.choose_category)


@router.message(PicrandomState.choose_category, F.text.casefold().in_(('sfw', 'nsfw')))
async def one_category(message: Message, state: FSMContext) -> None:
    category = message.text.lower()
    tags = categories[category]
    tags_list = ", ".join(tags)
    await message.answer(
        text=f'Please list the tags you are interested in (listed below) separated by spaces or commas, or select all.'
             f'\nList of tags: {html.italic(tags_list)}',
        reply_markup=picrandom_kb.all_categories)
    await state.update_data(category=category)
    await state.set_state(PicrandomState.choose_tag)


@router.message(PicrandomState.choose_category, F.text.casefold() == 'i want everything!')
async def both_categories(message: Message, state: FSMContext) -> None:
    await message.answer(
        text=f'That\'s right choice!',
        reply_markup=picrandom_kb.both_categories)
    await state.set_state(PicrandomState.both)


@router.message(PicrandomState.choose_category)
async def and_you_dont_seem_to_understand(message: Message) -> None:
    await message.answer(text='I don\'t understand...')


@router.message(PicrandomState.choose_tag)
async def choose_tag(message: Message, state: FSMContext) -> None:
    """
    Here the user lists the tags they need, then the validation of the data provided by the user is performed.
    The length of the user's message is limited to 350 characters.
    """
    user_message = message.text.lower()[:350]
    data = await state.get_data()
    category = data['category']
    entered_tags = user_message.replace(',', ' ').split()
    if entered_tags == ['select', 'all']:
        chosen_tags = categories[category]
    else:
        chosen_tags = []
        for tag in entered_tags:
            if tag in categories[category]:
                chosen_tags.append(tag)
    if chosen_tags:
        chosen_list = "all" if len(chosen_tags) == len(categories[category]) else ", ".join(chosen_tags)
        await message.answer(text=f'Selected tags: <i>{chosen_list}</i>', reply_markup=picrandom_kb.one_category)
        await state.update_data(tags=chosen_tags)
        await state.set_state(PicrandomState.one_category)
        await get_pict(message, category, chosen_tags)
    else:
        await message.answer(text='Tags were entered incorrectly.')


@router.message(PicrandomState.one_category)
async def random_one_category(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category = data['category']
    tags = data['tags']
    await get_pict(message, category, tags)


@router.message(PicrandomState.both)
async def random_both_categories(message: Message, state: FSMContext) -> None:
    user_message = message.text.lower()
    if user_message in ('sfw', 'nsfw'):
        category = user_message
        tags = categories[category]
        await get_pict(message, category, tags)
