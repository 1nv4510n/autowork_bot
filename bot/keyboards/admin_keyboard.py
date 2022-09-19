from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.enums import ApproveActions
from bot.db.models import ApplicationsEntry
from bot.cbdata import ApplyFactory, ApproveFactory

def make_admin_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='📨 Заявки', callback_data='applications'),
        InlineKeyboardButton(text='📈 Статистика работников', callback_data='employee_stats')
    )
    keyboard.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='back_menu'))
    
    return keyboard.as_markup()

def make_applications_keyboard(applications: List[ApplicationsEntry]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    for application in applications:
        keyboard.row(
            InlineKeyboardButton(
                text=application.full_name, 
                callback_data=ApplyFactory(telegram_id=application.telegram_id, full_name=application.full_name).pack()
            )
        )
    keyboard.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='back_admin_menu'))    
    
    return keyboard.as_markup()

def make_apply_user_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text='Да', callback_data=ApproveFactory(telegram_id=telegram_id, action=ApproveActions.yes).pack()),
        InlineKeyboardButton(text='Нет', callback_data=ApproveFactory(telegram_id=telegram_id, action=ApproveActions.no).pack())
    )
    keyboard.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='back_applications'))
    
    return keyboard.as_markup()

def make_back_admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⬅️ Назад', callback_data='back_admin_menu')]])