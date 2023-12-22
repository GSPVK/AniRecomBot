import requests
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from anirecombot.scraper import create_recommendations
from anirecombot.keyboards import main_kb, recomm_kb
from anirecombot.states.ani_recoms import RecommendationState

from redis.asyncio.client import Redis

router = Router()


async def create_recs(message: Message, state: FSMContext, mal_nickname: str, redis: Redis):
    """
    Insert recommendations into the database. Title - mal_nickname
    """
    search_msg = await message.answer(
        text=f"Let me conjure some recommendations, <b>{mal_nickname}-san!</b>\n"
             f"the first time it should take approx. 20-30 seconds\n"
             f"But while they are being generated, you can go back and do something else!"
    )

    # If you want to create a loading animation, then send the bot a GIF and insert the received file_id into
    # the animation parameter below, then uncomment the lines.
    #
    # anim = await message.answer_animation(
    #     animation='FILE_ID',
    #     reply_markup=recomm_kb.go_back_while_generating
    # )

    await redis.set(str(message.from_user.id), 'generating')
    cards = await sync_to_async(create_recommendations)(mal_nickname)
    await redis.rpush(mal_nickname, *cards)

    # await anim.delete()
    await search_msg.edit_text(text='Done!')
    await redis.delete(str(message.from_user.id))

    if await state.get_state() in ('RecommendationState:recomms', 'RecommendationState:scroll_recs'):
        card = await redis.lpop(mal_nickname)
        await message.answer(card, reply_markup=recomm_kb.scroll_recs)


@router.message(F.text.casefold() == 'anime recommendations')
async def recommended_anime_list(message: Message, state: FSMContext, redis: Redis) -> None:
    is_generating = await redis.get(str(message.from_user.id))
    if is_generating:
        await message.answer(text='Recommendations are not ready yet!', reply_markup=main_kb.main)
    else:
        await message.answer(text='Enter your\'s MAL nickname:', reply_markup=recomm_kb.go_back)
        await state.set_state(RecommendationState.recomms)


@router.message(RecommendationState.recomms)
async def get_recommendations(message: Message, state: FSMContext, redis: Redis) -> None:
    """
    Get recommendations for the user.

    The code first checks if the user exists in the database (first "if").
    If the user is not in the database, then the entered message is checked for correctness.
    If the message is correct, it generates recommendations and transitions to the "scroll_recs" state.
    Else, it sends a message stating that the specified account doesn't exist on MyAnimeList.
    """
    user_message = message.text.lower()

    if await redis.exists(user_message):
        mal_nickname = user_message
        await state.update_data(mal_nickname=mal_nickname)
        await message.answer(text=f'Welcome back, <b>{mal_nickname}-san!</b>')

        card = await redis.lpop(mal_nickname)
        await message.answer(card, reply_markup=recomm_kb.scroll_recs)
        await state.set_state(RecommendationState.scroll_recs)

    else:
        mal_acc = requests.get(f'https://api.jikan.moe/v4/users/{user_message}')

        if mal_acc.status_code == 200 and mal_acc.json().get('data'):
            mal_nickname = user_message
            await state.update_data(mal_nickname=mal_nickname)
            await create_recs(message=message, state=state, mal_nickname=mal_nickname, redis=redis)
            await state.set_state(RecommendationState.scroll_recs)
        else:
            await message.answer(text=f"Account doesn't exist.")


@router.message(RecommendationState.scroll_recs, F.text.casefold() == "next")
async def scroll(message: Message, state: FSMContext, redis: Redis) -> None:
    """
    Interaction with the generated table of recommendations.
    """
    data = await state.get_data()
    mal_nickname = data['mal_nickname']

    card = await redis.lpop(mal_nickname)
    if card is None:
        await message.answer(text='The End Of Recommendations!', reply_markup=main_kb.main)
        await state.clear()
    else:
        await message.answer(card, reply_markup=recomm_kb.scroll_recs)
        await state.set_state(RecommendationState.scroll_recs)


@router.message(RecommendationState.scroll_recs, F.text.casefold() == "update recs")
async def update_recs(message: Message, state: FSMContext, redis: Redis) -> None:
    data = await state.get_data()
    mal_nickname = data['mal_nickname']
    await redis.delete(mal_nickname)
    await create_recs(message=message, state=state, mal_nickname=mal_nickname, redis=redis)


@router.message(RecommendationState.scroll_recs)
async def and_you_dont_seem_to_understand(message: Message) -> None:
    await message.answer(text='I don\'t understand...')
