from aiogram.fsm.state import State, StatesGroup


class PicrandomState(StatesGroup):
    choose_category = State()
    choose_tag = State()
    one_category = State()
    both = State()
