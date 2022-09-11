from aiogram.fsm.state import State, StatesGroup

class RegisterStates(StatesGroup):
    enter_name = State()