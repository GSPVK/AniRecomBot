from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from anirecombot.keyboards import recomm_kb

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    /start command handler.
    """
    await message.answer('Welcome to AniRecomBot! Here you can get anime recommendations, pictures, quotes and so on.',
                         reply_markup=recomm_kb.main)
