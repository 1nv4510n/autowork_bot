import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from magic_filter import F
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .utils.logging import log

from bot.commands import set_commands
from bot.configreader import config
from bot.middlewares.db_middleware import DbSessionMiddleware

from bot.handlers import users_router, admins_router


async def main():
    # Creating DB engine for PostgreSQL
    engine = create_async_engine(config.postgres_dsn, future=True, echo=False)

    # Creating DB connections pool
    db_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Creating bot and its dispatcher
    bot = Bot(token=config.bot_token, parse_mode="HTML")
    if config.custom_bot_api:
        bot.session.api = TelegramAPIServer.from_base(config.custom_bot_api, is_local=True)

    # Choosing FSM storage
    if config.bot_fsm_storage == "memory":
        dp = Dispatcher(storage=MemoryStorage())
    else:
        dp = Dispatcher(storage=RedisStorage.from_url(config.redis_dsn))

    # Allow interaction in private chats (not groups or channels) only
    dp.message.filter(F.chat.type == "private")

    # Register middlewares
    dp.message.middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.outer_middleware(DbSessionMiddleware(db_pool))
    dp.message.outer_middleware(DbSessionMiddleware(db_pool))

    # Register /-commands in UI
    await set_commands(bot)
    
    dp.include_router(users_router)
    dp.include_router(admins_router)

    try:
        if not config.webhook_domain:
            log.info('BOT STARTED!')
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        else:
            # Suppress aiohttp access log completely
            aiohttp_logger = logging.getLogger("aiohttp.access")
            aiohttp_logger.setLevel(logging.CRITICAL)

            # Setting webhook
            await bot.set_webhook(
                url=config.webhook_domain + config.webhook_path,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )

            # Creating an aiohttp application
            app = web.Application()
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.webhook_path)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=config.app_host, port=config.app_port)
            await site.start()
            log.info('BOT STARTED')
            # Running it forever
            await asyncio.Event().wait()
    finally:
        log.info('BOT STOPPED')
        await bot.session.close()