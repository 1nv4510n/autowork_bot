from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def make_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text='💼 Работать', callback_data='start_work'),
        InlineKeyboardButton(text='📊 Статистика', callback_data='statistics')
    )
    keyboard.row(InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings'))
    keyboard.row(InlineKeyboardButton(text='🚫 Выход', callback_data='exit_menu'))
    
    return keyboard.as_markup()
    
def make_settings_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text='📜 Изменить URL таблицы', callback_data='edit_spreadsheet'),
        InlineKeyboardButton(text='📝 Изменить имя листа', callback_data='edit_sheetname')
    )
    keyboard.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='back_menu'))
    
    return keyboard.as_markup()

def make_work_choice_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(InlineKeyboardButton(text='Вручную', callback_data='classic_work'))
    keyboard.row(InlineKeyboardButton(text='Импорт из файла', callback_data='file_work'))
    keyboard.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='back_menu'))
    
    return keyboard.as_markup()

def make_statistis_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⬅️ Назад', callback_data='back_menu')]])