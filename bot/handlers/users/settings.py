from aiogram import Router, html
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.requests import get_spreadsheet_url, get_sheet_name, update_sheet_name, update_spreadsheet_url
from bot.keyboards.default_keyboard import make_settings_menu_keyboard

from .states.settings_states import SettingsStates

router = Router()

@router.callback_query(text='edit_spreadsheet')
async def edit_spreadsheet_url_callback(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.set_state(SettingsStates.enter_spreadsheet)
    current_url = await get_spreadsheet_url(session, call.from_user.id)
    await call.message.delete()
    if current_url is not None:
        await call.message.answer(f"{html.link('Текущая таблица', current_url)}\n\nВведите новую ссылку, либо введите /cancel для отмены")
    else:
        await call.message.answer('Введите ссылку на Google таблицу, либо введите /cancel для отмены')
        
@router.callback_query(text='edit_sheetname')
async def edit_sheet_name_callback(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.set_state(SettingsStates.enter_sheetname)
    current_sheetname = await get_sheet_name(session, call.from_user.id)
    await call.message.delete()
    if current_sheetname is not None:
        await call.message.answer(f"Текущее имя листа: {current_sheetname}\n\nВведите новое имя, либо введите /cancel для отмены")
    else:
        await call.message.answer('Введите имя листа, либо введите /cancel для отмены')
        
@router.message(SettingsStates.enter_spreadsheet)
async def enter_spreadsheet_url_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    spreadsheet_url = message.text
    if 'docs.google.com/' not in spreadsheet_url:
        await message.answer('Проверьте правильность ссылки и отправьте заного')
    else:
        await update_spreadsheet_url(session, message.from_user.id, spreadsheet_url)
        await state.clear()
        await message.answer('✔️ Успешно')
        await message.answer('Настройки', reply_markup=make_settings_menu_keyboard())
        
@router.message(SettingsStates.enter_sheetname)
async def enter_sheetname_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    sheetname = message.text
    await update_sheet_name(session, message.from_user.id, sheetname)
    await state.clear()
    await message.answer('✔️ Успешно')
    await message.answer('Настройки', reply_markup=make_settings_menu_keyboard())