from aiogram import Router

from .default import router as default_router
from .settings import router as settings_router
from .work import router as work_router
from .statistics import router as statistics_router

users_router = Router()
users_router.include_router(default_router)
users_router.include_router(settings_router)
users_router.include_router(work_router)
users_router.include_router(statistics_router)