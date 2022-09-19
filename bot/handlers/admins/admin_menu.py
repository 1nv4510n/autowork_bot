from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.db.models import UsersEntry

from bot.enums import ApproveActions
from bot.keyboards.admin_keyboard import make_admin_menu_keyboard, make_applications_keyboard, make_apply_user_keyboard, make_back_admin_menu_keyboard
from bot.keyboards.default_keyboard import make_main_menu_keyboard

from bot.db.requests import get_all_users, get_applications_list, add_user, delete_application
from bot.cbdata import ApplyFactory, ApproveFactory

router = Router()

@router.callback_query(text=['admin_menu', 'back_admin_menu'])
async def show_admin_menu_callback(call: CallbackQuery) -> None:
    await call.message.edit_text('Меню администратора', reply_markup=make_admin_menu_keyboard())
    
@router.callback_query(text=['applications', 'back_applications'])
async def show_applications_callback(call: CallbackQuery, session: AsyncSession) -> None:
    applications = await get_applications_list(session)
    if applications == []:
        await call.answer('Заявки на вступление отсуствуют')
    else:
        await call.message.edit_text(text='Список заявок', reply_markup=make_applications_keyboard(applications))
    
@router.callback_query(ApplyFactory.filter())
async def show_approve_choice_callback(call: CallbackQuery, callback_data: ApplyFactory) -> None:
    apply_user_id = callback_data.telegram_id
    name = callback_data.full_name
    
    await call.message.edit_text(
        text=f'<b>{name}</b>\n\nВы хотите одобрить заявку на вступление?',
        reply_markup=make_apply_user_keyboard(apply_user_id)
    )
    
@router.callback_query(ApproveFactory.filter())
async def approve_user_callback(call: CallbackQuery, bot: Bot, callback_data: ApproveFactory, session: AsyncSession) -> None:
    apply_user_id = callback_data.telegram_id
    action: ApproveActions = callback_data.action
    
    if action == ApproveActions.yes:
        name = await delete_application(session, apply_user_id)
        await add_user(session, apply_user_id, name)
        await bot.send_message(apply_user_id, text='Ваша заявка была успешно одобрена!')
        await bot.send_message(apply_user_id, text='Добро пожаловать', reply_markup=make_main_menu_keyboard())
    else:
        await bot.send_message(apply_user_id, text='Ваша заявка была отклонена. Вы можете повторить отправку заявки')
        await delete_application(session, apply_user_id)
        
    applications = await get_applications_list(session)
    if applications == []:
        await call.message.edit_text('Меню администратора', reply_markup=make_admin_menu_keyboard())
    else:
        await call.message.edit_text(text='Список заявок', reply_markup=make_applications_keyboard(applications))
        
@router.callback_query(text='employee_stats')
async def employee_stats_callback(call: CallbackQuery, session: AsyncSession) -> None:
    stats = '<b>{name}</b>\n<i>Количество заполненых строчек: <b>{line_count}</b></i>\n'
    stats_message = ''
    users = await get_all_users(session)
    user: UsersEntry
    for user in users:
        stats_message += stats.format(name=user.full_name, line_count=user.total_lines)
        
    await call.message.edit_text(stats_message, reply_markup=make_back_admin_menu_keyboard())