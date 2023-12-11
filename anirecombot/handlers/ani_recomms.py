import requests
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Text

from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from anirecombot.sql_db import recs_db
from anirecombot.scraper import create_recommendations
from anirecombot.keyboards import main_kb, recomm_kb
from anirecombot.states.ani_recoms import RecommendationState

router = Router()
users_recs_dict = {}


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


@router.message(F.text.casefold() == 'anime recommendations')
async def recommended_anime_list(message: Message, state: FSMContext) -> None:
    await message.answer(text='Enter your\'s MAL nickname:', reply_markup=recomm_kb.go_back)
    await state.set_state(RecommendationState.recomms)


@router.message(RecommendationState.recomms)
async def get_recommendations(message: Message, state: FSMContext) -> None:
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
        await state.set_state(RecommendationState.scroll_recs)

    else:
        get_req = requests.get(f'https://api.jikan.moe/v4/users/{user_message}')

        if get_req.status_code == 200 and get_req.json().get('data'):
            mal_nickname = user_message
            await state.update_data(mal_nickname=mal_nickname)
            await create_recs(message=message, mal_nickname=mal_nickname)
            await state.set_state(RecommendationState.scroll_recs)
        else:
            await message.answer(text=f"Account doesn't exist.")


@router.message(RecommendationState.scroll_recs, F.text.casefold() == "next")
async def next_title(message: Message, state: FSMContext) -> None:
    """
    Interaction with the generated table of recommendations.

    Update the table (delete the old one, create new)
    Return to main menu
    Show next recommendation.
    """
    data = await state.get_data()
    mal_nickname = data['mal_nickname']

    try:
        await message.answer(next(users_recs_dict[mal_nickname]))
    except KeyError:
        await message.answer(text='Something went wrong...', reply_markup=main_kb.main)
    except StopIteration:
        await message.answer(text='The End Of Recommendations!', reply_markup=main_kb.main)
        users_recs_dict.pop(mal_nickname)
        await state.clear()


@router.message(RecommendationState.scroll_recs, F.text.casefold() == "update recs")
async def update_recs(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    mal_nickname = data['mal_nickname']
    recs_db.del_table(mal_nickname)
    await create_recs(message=message, mal_nickname=mal_nickname)


@router.message(RecommendationState.scroll_recs)
async def and_you_dont_seem_to_understand(message: Message) -> None:
    await message.answer(text='I don\'t understand...')


@router.message(Text(('Next', 'Update recs')))
async def return_to_menu(message: Message) -> None:
    """
    In case of restarting the bot.

    The state loses the user, so clicking on buttons will have no effect.
    """
    await message.answer(text='Something went wrong...', reply_markup=main_kb.main)
