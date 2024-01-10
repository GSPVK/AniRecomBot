from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.animation)
async def echo_animation(message: Message) -> None:
    """
    Response with file id.
    """
    await message.reply(f'file id = "{message.animation.file_id}"')


@router.message(F.sticker)
async def echo_gif(message: Message) -> None:
    """
    Response with the same sticker.
    """
    await message.reply_sticker(message.sticker.file_id)


@router.message()
async def echo_message(message: Message) -> None:
    """
    Response with the same message with case change.
    """
    await message.answer(message.text.swapcase())
