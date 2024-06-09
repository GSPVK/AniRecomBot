from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from anirecombot.keyboards import main_kb

router = Router()


@router.message(F.text.casefold() == 'main menu')
async def return_to_menu(message: Message, state: FSMContext) -> None:
    if await state.get_state():
        await message.answer(text='I hope you found something!', reply_markup=main_kb.main)
        await state.clear()
    else:
        await message.answer(text='Something went wrong...', reply_markup=main_kb.main)


@router.message(F.text.casefold() == 'go back')
async def go_back_to_menu(message: Message, state: FSMContext) -> None:
    if await state.get_state():
        await message.answer(text='s..sure..', reply_markup=main_kb.main)
        await state.clear()
    else:
        await message.answer(text='Something went wrong...', reply_markup=main_kb.main)
