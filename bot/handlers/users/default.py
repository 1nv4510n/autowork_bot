from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound

from bot.configreader import config
from bot.db.requests import is_user_exists, add_user, get_spreadsheet_url, get_sheet_name
from bot.keyboards.default_keyboard import make_main_menu_keyboard, make_settings_menu_keyboard, \
    make_work_choice_keyboard
from bot.product_parser.sheets import GoogleSheets

from .states.register_states import RegisterStates
from .states.settings_states import SettingsStates
from .states.work_states import WorkStates

router = Router()

@router.message(commands=['start'])
async def start_handler(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if not await is_user_exists(session, message.from_user.id):
        await state.set_state(RegisterStates.enter_name)
        await message.answer('Введите ваше ФИО через пробел')
    else:
        await message.answer('Добро пожаловать!', reply_markup=make_main_menu_keyboard()) 

@router.message(RegisterStates.enter_name)
async def enter_name_handler(message: Message, session: AsyncSession, state: FSMContext) -> None:
    full_name  = message.text
    if (len(full_name.split(' ')) != 3):
        await message.answer('Ошибка! Введите ваше ФИО через пробел')
    else:
        await add_user(session, message.from_user.id, full_name)
        await message.answer('Регистрация прошла успешно!', reply_markup=make_main_menu_keyboard())
        await state.clear()
        
@router.callback_query(text='settings')
async def settings_callback(call: CallbackQuery) -> None:
    await call.message.edit_text(text='Настройки', reply_markup=make_settings_menu_keyboard())
    
@router.callback_query(text='start_work')
async def start_work_callback(call: CallbackQuery, session: AsyncSession) -> None:
    spreadsheet_url = await get_spreadsheet_url(session, call.from_user.id)
    worksheet_name = await get_sheet_name(session, call.from_user.id)
    
    if worksheet_name is not None and spreadsheet_url is not None:
        try:
            GoogleSheets(spreadsheet_url=spreadsheet_url, worksheet_name=worksheet_name)
        except SpreadsheetNotFound:
            await call.message.answer(f'Ошибка! Таблица не найдена, проверьте URL таблицы в настройках, а также добавьте сервисный аккаунт {config.service_account} как редактора',
                                      reply_markup=make_main_menu_keyboard())
            await call.message.delete()
            return
        except WorksheetNotFound:
            await call.message.answer(f'Ошибка! Проверьте имя листа в настройках, а также добавьте сервисный аккаунт {config.service_account} как редактора',
                                      reply_markup=make_main_menu_keyboard())
            await call.message.delete()
            return
    else:
        await call.message.answer(f'Ошибка! Заполните URL таблицы и имя листа в настройках, а также добавьте сервисный аккаунт {config.service_account} как редактора',
                                  reply_markup=make_main_menu_keyboard())
        await call.message.delete()
        return

    await call.message.edit_text(text='Выберите режим работы', reply_markup=make_work_choice_keyboard())
    
@router.callback_query(text='back_menu')
async def back_main_menu_callback(call: CallbackQuery) -> None:
    await call.message.edit_text(text='Добро пожаловать!', reply_markup=make_main_menu_keyboard())
    
@router.callback_query(text='exit_menu')
async def exit_menu_callback(call: CallbackQuery) -> None:
    await call.answer(text='Успешно')
    await call.message.delete()
    
@router.message(SettingsStates.enter_spreadsheet, commands=['cancel'])
@router.message(SettingsStates.enter_sheetname, commands=['cancel'])
async def settings_cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Настройки', reply_markup=make_settings_menu_keyboard())

@router.message(WorkStates.send_city, commands=['cancel', 'skip']) 
@router.message(WorkStates.send_file, commands=['cancel', 'skip']) 
@router.message(WorkStates.send_product_name, commands=['cancel', 'skip']) 
@router.message(WorkStates.send_website, commands=['cancel', 'skip']) 
@router.message(WorkStates.send_price, commands=['cancel', 'skip']) 
@router.message(WorkStates.send_inn, commands=['cancel', 'skip']) 
async def work_cancel_handler(message: Message, state: FSMContext) -> None:
    if message.text == '/cancel':
        await state.clear()
        await message.answer('Добро пожаловать', reply_markup=make_main_menu_keyboard())
    if message.text == '/skip':
        await state.set_state(WorkStates.send_website)
        await message.answer('Вы пропустили заполнение строчки')
        await message.answer('Отправьте ссылку на товар')