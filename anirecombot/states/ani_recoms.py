from aiogram.fsm.state import State, StatesGroup


class RecommendationState(StatesGroup):
    recomms = State()
    scroll_recs = State()
