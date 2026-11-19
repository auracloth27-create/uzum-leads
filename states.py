from aiogram.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    language = State()
    name = State()
    seller = State()
    age = State()
    phone = State()
