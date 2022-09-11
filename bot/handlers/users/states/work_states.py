from aiogram.fsm.state import State, StatesGroup

class WorkStates(StatesGroup):
    send_file = State()
    
    send_inn = State()
    send_website = State()
    send_city = State()
    send_product_name = State()
    send_price = State()