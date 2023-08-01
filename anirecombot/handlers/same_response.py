from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.animation)
async def echo_animation(message: Message):
    """
    Response with the same gif.
    """
    await message.reply_animation(message.animation.file_id)


@router.message(F.sticker)
async def echo_gif(message: Message):
    """
    Response with the same sticker.
    """
    await message.reply_sticker(message.sticker.file_id)


@router.message()
async def echo_message(message: Message):
    """
    Response with the same message with case change.
    """
    await message.answer(message.text.swapcase())
