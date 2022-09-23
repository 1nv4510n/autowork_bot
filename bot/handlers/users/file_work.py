from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, ContentType, InputMediaDocument
from aiogram.filters import ContentTypesFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlparse
from bot.configreader import config
from bot.db.requests import add_ogrn, delete_ogrn, get_sheet_name, get_spreadsheet_url, add_line_count, get_ogrn
from io import BytesIO

from .states.work_states import WorkStates
from bot.product_parser.rusprofile import RusProfileParser
from bot.product_parser.sheets import GoogleSheets

router = Router()

rusprofile_parser = RusProfileParser()

@router.callback_query(text='file_work')
async def file_work_mode_callback(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await call.message.answer(
        text=f'Внимание! Перед началом работы необходимо добавить аккаунт <b>{config.service_account}</b> в таблицу как редактора!\n\n \
        Чтобы выйти из режима работы, введите /cancel'
    )
    await call.message.delete()
    await state.set_state(WorkStates.send_file)
    
@router.message(ContentTypesFilter(content_types=[ContentType.DOCUMENT]))
async def document_message_handler(message: Message, bot: Bot) -> None:
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    result: BytesIO = await bot.download_file(file_path)
    print(result.read().decode('UTF-8'))