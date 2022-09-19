from typing import Union, List

from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.requests import get_admin_list

class AdminFilter(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        admins = await get_admin_list(session)
        
        if message.from_user.id not in admins:
            await message.answer('У вас нет доступа!')
            return False
        return True