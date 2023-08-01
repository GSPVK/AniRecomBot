import requests
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from anirecombot.sql_db import recs_db
from anirecombot.scraper import create_recommendations
from anirecombot.keyboards import recomm_kb

router = Router()
users_recs_dict = {}


class Form(StatesGroup):
    recomms = State()
    scroll_recs = State()


def form_cards(mal_nickname: str):
    records = recs_db.get_all_recs(mal_nickname)

    for row in records:
        card = f'<b>Title:</b> {row[1]}\n' \
               f'<b>Genres:</b> {row[2]}\n' \
               f'<b>Plan To Watch:</b> {row[3]}\n\n' \
               f'<b>Synopsis:</b> {row[4]}\n\n' \
               f'{row[5]}'

        yield card


async def create_recs(message: Message, mal_nickname: str):
    """
    Insert a new table with a list of recommendations into the database. Title - mal_nickname
    """
    search = await message.answer(
        text=f"Let me conjure some recommendations, <b>{mal_nickname}-san!</b>\n"
             f"the first time it should take approx. 20 seconds")
    anim = await message.answer_animation(
        animation='CgACAgIAAxkBAAID1mQQnJJIpIBe74w-kMTze2ZfRiqPAAJXLAAC4oqJSKBUjy8gxIHzLwQ')

    await sync_to_async(create_recommendations)(mal_nickname)
    await anim.delete()
    await search.edit_text(text='Done!')
    users_recs_dict[mal_nickname] = form_cards(mal_nickname)
    await message.answer(next(users_recs_dict[mal_nickname]),
                         reply_markup=recomm_kb.scroll_recs)


@router.message(Text('Anime Recommendations'))
async def recommended_anime_list(message: Message, state: FSMContext):
    await message.answer(text='Enter your\'s MAL nickname:', reply_markup=recomm_kb.go_back)
    await state.set_state(Form.recomms)


@router.message(Form.recomms)
async def get_recommendations(message: Message, state: FSMContext):
    """
    Get recommendations for the user.

    The code first checks if the user exists in the database (first "if")
    If the user is not in the database, then the entered message is checked for correctness.
    If the message is correct, it generates recommendations and transitions to the "Form.scroll_recs" state.
    Else, it sends a message stating that the specified account doesn't exist on MyAnimeList.
    """
    user_message = message.text.lower()

    if recs_db.is_exist(user_message):
        mal_nickname = user_message
        await state.update_data(mal_nickname=mal_nickname)
        await message.answer(text=f'Welcome back, <b>{mal_nickname}-san!</b>')

        try:
            users_recs_dict[mal_nickname]
        except KeyError:
            users_recs_dict[mal_nickname] = form_cards(mal_nickname)
        await message.answer(next(users_recs_dict[mal_nickname]),
                             reply_markup=recomm_kb.scroll_recs)
        await state.set_state(Form.scroll_recs)

    else:
        get_req = requests.get(f'https://api.jikan.moe/v4/users/{user_message}')

        if get_req.status_code == 200 and get_req.json().get('data'):
            mal_nickname = user_message
            await state.update_data(mal_nickname=mal_nickname)
            await create_recs(message=message, mal_nickname=mal_nickname)
            await state.set_state(Form.scroll_recs)

        elif user_message == 'go back':
            await message.answer(f's..sure..', reply_markup=recomm_kb.main)
            await state.clear()

        else:
            await message.answer(text=f"Account doesn't exist.")


@router.message(Form.scroll_recs)
async def next_title(message: Message, state: FSMContext):
    """
    Interaction with the generated table of recommendations.

    Update the table (delete the old one, create new)
    Return to main menu
    Show next recommendation.
    """
    user_message = message.text.lower()
    data = await state.get_data()
    mal_nickname = data['mal_nickname']

    if user_message == 'update recs':
        recs_db.del_table(mal_nickname)
        await create_recs(message=message, mal_nickname=mal_nickname)

    elif user_message == 'main menu':
        await message.answer(text='I hope you found something!', reply_markup=recomm_kb.main)
        await state.clear()

    else:
        try:
            await message.answer(next(users_recs_dict[mal_nickname]))
        except KeyError:
            await message.answer(text='Something went wrong...', reply_markup=recomm_kb.main)
        except StopIteration:
            await message.answer(text='The End Of Recommendations!', reply_markup=recomm_kb.main)
            users_recs_dict.pop(mal_nickname)
            await state.clear()


@router.message(Text(('Next', 'Main Menu', 'Update recs', 'Go back')))
async def return_to_menu(message: Message):
    """
    In case of restarting the bot.

    The state loses the user, so clicking on buttons will have no effect.
    """
    await message.answer(text='Something went wrong...', reply_markup=recomm_kb.main)
