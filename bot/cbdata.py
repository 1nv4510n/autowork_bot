from aiogram.filters.callback_data import CallbackData
from bot.enums import ApproveActions

class ApplyFactory(CallbackData, prefix='apply'):
    telegram_id: int
    full_name: str
    
class ApproveFactory(CallbackData, prefix='approve'):
    telegram_id: int
    action: ApproveActions