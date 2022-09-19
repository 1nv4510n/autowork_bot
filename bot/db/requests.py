from typing import Dict, List, Optional
from contextlib import suppress
from urllib import request

from sqlalchemy import select, update, desc, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from bot.db.models import ApplicationsEntry, UsersEntry, OgrnListEntry

# get data

async def get_applications_list(session: AsyncSession) -> List[ApplicationsEntry]:
    request = await session.execute(
        select(ApplicationsEntry)
    )
    return request.scalars().all()

async def get_ogrn(session: AsyncSession, website: str) -> Optional[str]:
    request = await session.execute(
        select(OgrnListEntry).filter_by(website=website)
    )
    
    entry = request.scalars().first()
    if entry is not None:
        return entry.ogrn
    else:
        return None

async def is_user_exists(session: AsyncSession, telegram_id: int) -> bool:
    request = await session.execute(
        select(UsersEntry).filter_by(telegram_id=telegram_id)
    )
    return request.scalars().first() is not None

async def is_user_apply_exists(session: AsyncSession, telegram_id: int) -> bool:
    request = await session.execute(
        select(ApplicationsEntry).filter_by(telegram_id=telegram_id)
    )
    return request.scalars().first() is not None

async def get_admin_list(session: AsyncSession) -> List[int]:
    request = await session.execute(
        select(UsersEntry).where(UsersEntry.is_admin == True)
    )
    
    admins: UsersEntry = request.scalars().all()

    return [admin.telegram_id for admin in admins]

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

async def get_all_users(session: AsyncSession) -> List[UsersEntry]:
    request = await session.execute(
        select(UsersEntry)
    )
    return request.scalars().all()
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
        
async def add_application(session: AsyncSession, telegram_id: int, full_name: str) -> None:
    entry = ApplicationsEntry()
    entry.telegram_id = telegram_id
    entry.full_name = full_name
    session.add(entry)
    with suppress(IntegrityError):
        await session.commit()
        
async def add_ogrn(session: AsyncSession, website: str, ogrn: str) -> None:
    entry = OgrnListEntry()
    entry.website = website
    entry.ogrn = ogrn
    session.add(entry)
    with suppress(IntegrityError):
        await session.commit()
        
async def delete_application(session: AsyncSession, telegram_id: int) -> str:
    request = await session.execute(
        select(ApplicationsEntry.full_name).where(ApplicationsEntry.telegram_id == telegram_id)
    )
    
    await session.execute(
        delete(ApplicationsEntry).where(ApplicationsEntry.telegram_id == telegram_id)
    )
    await session.commit()
    return request.scalar()

async def delete_ogrn(session: AsyncSession, ogrn: str) -> None:
    await session.execute(
        delete(OgrnListEntry).where(OgrnListEntry.ogrn == ogrn)
    )
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