from typing import Dict, List, Optional
from contextlib import suppress

from sqlalchemy import select, update, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from bot.db.models import UsersEntry

# get data

async def is_user_exists(session: AsyncSession, telegram_id: int) -> bool:
    request = await session.execute(
        select(UsersEntry).filter_by(telegram_id=telegram_id)
    )
    return request.scalars().first() is not None

async def get_spreadsheet_url(session: AsyncSession, telegram_id: int) -> str:
    request = await session.execute(
        select(UsersEntry.spreadsheet_url).where(UsersEntry.telegram_id == telegram_id)
    )
    
    return request.scalar()

async def get_sheet_name(session: AsyncSession, telegram_id: int) -> str:
    request = await session.execute(
        select(UsersEntry.sheet_name).where(UsersEntry.telegram_id == telegram_id)
    )
    
    return request.scalar()

async def get_user(session: AsyncSession, telegram_id: int) -> UsersEntry:
    request = await session.execute(
        select(UsersEntry).filter_by(telegram_id=telegram_id)
    )
    return request.scalars().first()

# modify data

async def add_user(session: AsyncSession, telegram_id: int, full_name: str) -> None:
    entry = UsersEntry()
    entry.telegram_id = telegram_id
    entry.full_name = full_name
    entry.total_lines = 0
    entry.is_admin = False
    session.add(entry)
    with suppress(IntegrityError):
        await session.commit()
        
async def update_spreadsheet_url(session: AsyncSession, telegram_id: int, spreadsheet_url: str) -> None:
    await session.execute(
        update(UsersEntry).where(UsersEntry.telegram_id == telegram_id).values(spreadsheet_url=spreadsheet_url)
    )
    with suppress(IntegrityError):
        await session.commit()
        
async def update_sheet_name(session: AsyncSession, telegram_id: int, sheet_name: str) -> None:
    await session.execute(
        update(UsersEntry).where(UsersEntry.telegram_id == telegram_id).values(sheet_name=sheet_name)
    )
    with suppress(IntegrityError):
        await session.commit()
        
async def add_line_count(session: AsyncSession, telegram_id: int, total: int) -> None:
    await session.execute(
        update(UsersEntry).where(UsersEntry.telegram_id == telegram_id).values(
            total_lines=UsersEntry.total_lines + total
        )
    )
    with suppress(IntegrityError):
        await session.commit()