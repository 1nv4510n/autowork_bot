from aiogram import Router
from bot.filters.admin_filter import AdminFilter

from .admin_menu import router as admin_menu_router

admins_router = Router()
admins_router.callback_query.filter(AdminFilter())
admins_router.message.filter(AdminFilter())

admins_router.include_router(admin_menu_router)