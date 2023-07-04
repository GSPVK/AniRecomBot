import asyncio
import logging
import requests

from random import choice

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Text
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from asgiref.sync import sync_to_async
from config_reader import config
from scraper import create_recommendations
from sql_db import RecommendationsDB

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode='HTML')
dp = Dispatcher(bot=bot)
recs_db = RecommendationsDB('../recs_db.db')


class Form(StatesGroup):
    recomms = State()
    scroll_recs = State()


def create_keyboards():
    keyboards_dict = {}
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text='Quote'),
        types.KeyboardButton(text='PicRandom'),
        types.KeyboardButton(text='B..Baka!')
    )
    builder.row(types.KeyboardButton(text='Anime Recommendations'))
    main_keyboard = builder.as_markup(resize_keyboard=True, input_field_placeholder='Choose wisely...')
    keyboards_dict['main_keyboard'] = main_keyboard

    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Next'),
                types.KeyboardButton(text='Main Menu'),
                types.KeyboardButton(text='Update recs'))
    next_button = builder.as_markup(resize_keyboard=True)
    keyboards_dict['next_button'] = next_button

    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Go back'))
    go_back = builder.as_markup(resize_keyboard=True)
    keyboards_dict['go_back'] = go_back

    return keyboards_dict


def form_cards(username):
    records = recs_db.get_all_recs(username)

    for row in records:
        card = f'<b>Title:</b> {row[1]}\n' \
               f'<b>Genres:</b> {row[2]}\n' \
               f'<b>Plan To Watch:</b> {row[3]}\n\n' \
               f'<b>Synopsis:</b> {row[4]}\n\n' \
               f'{row[5]}'

        yield card


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    /start command handler.
    """
    await message.answer('Welcome to AniRecomBot! Here you can get anime recommendations, pictures, quotes and so on.',
                         reply_markup=keyboards['main_keyboard'])


@dp.message(Text('Anime Recommendations'))
async def recommended_anime_list(message: types.Message, state: FSMContext):
    await message.answer(text='Enter your\'s MAL nickname:', reply_markup=keyboards['go_back'])
    await state.set_state(Form.recomms)


@dp.message(Form.recomms)
async def get_recommendations(message: Message, state: FSMContext):
    """
    Get recommendations for the user.

    The code first checks if the user exists in the database (first "if")
    If the user is not in the database, then the entered message is checked for correctness.
    If the message is correct, it generates recommendations and transitions to the "Form.scroll_recs" state.
    If the message is incorrect, it sends a message stating that the specified account doesn't exist on MyAnimeList.
    """
    user_message = message.text.lower()

    if recs_db.is_exist(user_message):
        await state.update_data(mal_nickname=user_message)
        mal_nickname = user_message
        await message.answer(text=f'Welcome back, <b>{mal_nickname}-san!</b>')

        try:
            users_recs_dict[message.from_user.id]
        except KeyError:
            users_recs_dict[message.from_user.id] = form_cards(mal_nickname)
        await message.answer(next(users_recs_dict[message.from_user.id]),
                             reply_markup=keyboards['next_button'])
        await state.set_state(Form.scroll_recs)

    else:
        get_req = requests.get(f'https://api.jikan.moe/v4/users/{user_message}')

        if get_req.status_code == 200 and get_req.json().get('data'):
            await state.update_data(mal_nickname=user_message)
            mal_nickname = user_message
            await create_recs(message=message, username=mal_nickname)
            await state.set_state(Form.scroll_recs)

        elif user_message == 'go back':
            await message.answer(f's..sure..', reply_markup=keyboards['main_keyboard'])
            await state.clear()

        else:
            await message.answer(text=f"Account doesn't exist.")
            await state.set_state(Form.recomms)


async def create_recs(message, username):
    """
    Insert a new table with a list of recommendations into the database. Title - username
    """
    search = await message.answer(
        text=f"Let me conjure some recommendations, <b>{username}-san!</b>\n"
             f"the first time it should take approx. 20 seconds")
    anim = await message.answer_animation(
        animation='CgACAgIAAxkBAAID1mQQnJJIpIBe74w-kMTze2ZfRiqPAAJXLAAC4oqJSKBUjy8gxIHzLwQ')

    await sync_to_async(create_recommendations)(username)
    await anim.delete()
    await search.edit_text(text='Done!')
    users_recs_dict[message.from_user.id] = form_cards(username)
    await message.answer(next(users_recs_dict[message.from_user.id]),
                         reply_markup=keyboards['next_button'])


@dp.message(Form.scroll_recs)
async def next_title(message: types.Message, state: FSMContext):
    """
    Interaction with the generated table of recommendations.

    Update the table (delete the old one, create new)
    Return to main menu
    Show next recommendation.
    """
    user_message = message.text.lower()
    data = await state.get_data()
    nickname = data['mal_nickname']

    if user_message == 'update recs':
        recs_db.del_table(nickname)
        await create_recs(message=message, username=nickname)

    elif user_message == 'main menu':
        await message.answer(text='I hope you found something!', reply_markup=keyboards['main_keyboard'])
        await state.clear()

    else:
        try:
            await message.answer(next(users_recs_dict[message.from_user.id]))
        except KeyError:
            await message.answer(text='Something went wrong...', reply_markup=keyboards['main_keyboard'])
        except StopIteration:
            await message.answer(text='The End Of Recommendations!', reply_markup=keyboards['main_keyboard'])
            users_recs_dict.pop(message.from_user.id)
            await state.clear()


@dp.message(Text(('Next', 'Main Menu', 'Update recs', 'Go back')))
async def return_to_menu(message: types.Message):
    """
    In case of restarting the bot.

    The state loses the user, so clicking on buttons will have no effect.
    """
    await message.answer(text='Something went wrong...', reply_markup=keyboards['main_keyboard'])


@dp.message(Text('Quote'))
async def send_quote(message: types.Message):
    """
    Get random quote from https://animechan.vercel.app/
    """
    data = requests.get('https://animechan.vercel.app/api/random').json()
    anime = data['anime']
    character = data['character']
    quote = data['quote']
    await message.answer(f'<b>Anime:</b> {anime}\n<b>Character:</b> {character}\n\n<i>{quote}</i>')


@dp.message(Text('PicRandom'))
async def random_image(message: types.Message):
    """
    Get random image from https://waifu.pics/docs
    """
    categories = ['awoo', 'waifu', 'neko']
    category = choice(categories)
    pic = requests.get(f'https://api.waifu.pics/sfw/{category}').json()
    url_pic = pic['url']
    await message.answer_photo(url_pic)


@dp.message(Text('B..Baka!'))
async def send_baka(message: types.Message):
    """
    Get "Baka" from https://catboys.com/api/
    """
    baka = requests.get('https://api.catboys.com/baka').json()
    url_baka = baka['url']
    await message.answer_animation(url_baka)


@dp.message(F.animation)
async def echo_animation(message: types.Message):
    """
    Response with the same gif.
    """
    await message.reply_animation(message.animation.file_id)


@dp.message(F.sticker)
async def echo_gif(message: types.Message):
    """
    Response with the same sticker.
    """
    await message.reply_sticker(message.sticker.file_id)


@dp.message()
async def echo_message(message: types.Message):
    """
    Response with the same message with case change.
    """
    await bot.send_message(message.from_user.id, message.text.swapcase())


async def main():
    """
    Start the polling process.
    """
    await dp.start_polling(bot)


if __name__ == "__main__":
    keyboards = create_keyboards()
    users_recs_dict = {}
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
