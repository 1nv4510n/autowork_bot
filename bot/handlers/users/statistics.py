from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.default_keyboard import make_statistis_keyboard
from bot.db.requests import get_user

router = Router()

@router.callback_query(text='statistics')
async def show_statistics_callback(call: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user(session, call.from_user.id)
    
    stats = '<b>{name}</b>\n\nКоличество заполненых строчек: {line_count}'
    
    await call.message.edit_text(
        text=stats.format(name=user.full_name, line_count=user.total_lines),
        reply_markup=make_statistis_keyboard()
    )