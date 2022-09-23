from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlparse

from bot.configreader import config
from bot.db.requests import add_ogrn, delete_ogrn, get_sheet_name, get_spreadsheet_url, add_line_count, get_ogrn

from .states.work_states import WorkStates
from bot.product_parser.rusprofile import RusProfileParser
from bot.product_parser.sheets import GoogleSheets

router = Router()

rusprofile_parser = RusProfileParser()

@router.callback_query(text='classic_work')
async def classic_work_mode_callback(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await call.message.answer(
        text=f'Внимание! Перед началом работы необходимо добавить аккаунт <b>{config.service_account}</b> в таблицу как редактора!\n\n \
        Чтобы выйти из режима работы, введите /cancel\n\nЧтобы пропустить заполнение строки, введите /skip'
    )
    await state.set_state(WorkStates.send_website)
    await state.set_data(
        {
            'googlesheets' : GoogleSheets(
                spreadsheet_url=await get_spreadsheet_url(session, call.from_user.id),
                worksheet_name=await get_sheet_name(session, call.from_user.id)
            ),
            'save_ogrn' : False
        }
    )
    
    await call.message.answer('Отправьте ссылку на товар')
    await call.message.delete()
    
@router.message(WorkStates.send_website)
async def send_website_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if 'http' not in message.text:
        await message.answer('Проверьте правильность ссылки и отправьте снова')
    else:  
        domain = urlparse(message.text).netloc
        ogrn = await get_ogrn(session, domain)
        if ogrn is not None:
            company_info = rusprofile_parser.search_by_inn(ogrn)
            if company_info['status'] == 'ERROR' or company_info['company_status'] == 'ERROR' or company_info['realiability'] == 'ERROR':
                await delete_ogrn(session, ogrn)
            else:
                await state.set_state(WorkStates.send_city)
                await state.update_data(product_url=message.text, company_info=company_info)
                await message.answer('Введите город')
                return
        await state.set_state(WorkStates.send_inn)
        await state.update_data(product_url=message.text, save_ogrn=True)
        await message.answer('Введите ИНН/КПП/ОГРН компании')
        
@router.message(WorkStates.send_inn)
async def send_inn_handler(message: Message, state: FSMContext) -> None:
    company_info = rusprofile_parser.search_by_inn(message.text)
    
    if company_info['status'] == 'ERROR':
        await message.answer('Ошибка! Компания не была найдена, либо их несколько в поиске! Введите ИНН/КПП/ОГРН заново')
        return
    if company_info['company_status'] == 'ERROR':
        await message.answer('Ошибка! Компания на данный момент не активна! Введите ИНН/КПП/ОГРН заново')
        return
    if company_info['realiability'] == 'ERROR':
        await message.answer('Ошибка! Надежность компании низкая! Введите ИНН/КПП/ОГРН заново')
        return
    
    await state.set_state(WorkStates.send_city)
    await state.update_data(company_info=company_info)
    await message.answer('Введите город')
    
@router.message(WorkStates.send_city)        
async def send_city_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(WorkStates.send_product_name)
    await state.update_data(product_city=message.text)
    await message.answer('Введите имя товара')
    
@router.message(WorkStates.send_product_name)        
async def send_product_name_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(WorkStates.send_price)
    await state.update_data(product_name=message.text)
    await message.answer('Введите цену товара указанную на сайте (используется точка)')
    
@router.message(WorkStates.send_price)        
async def send_price_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(product_price=message.text)
    
    current_data = await state.get_data()
    
    
    if current_data['save_ogrn']:
        await add_ogrn(
            session, urlparse(current_data['product_url']).netloc, current_data['company_info']['company_ogrn']
        )
        await state.update_data(save_ogrn=False)
    
    google_sheets: GoogleSheets = current_data['googlesheets']
    
    try:
        google_sheets.fill_line(current_data)
    except Exception as e:
        await message.answer(f'Ошибка заполнения строчки\n\n{e} Попробуйте заново')
    else:
        await message.answer('Строка успешно заполнена')
        await add_line_count(session, message.from_user.id, 1)
        
    await state.set_state(WorkStates.send_website)
    await message.answer('Отправьте ссылку на товар')