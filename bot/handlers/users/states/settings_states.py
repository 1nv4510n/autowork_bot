from aiogram.fsm.state import State, StatesGroup

class SettingsStates(StatesGroup):
    enter_spreadsheet = State()
    enter_sheetname = State()