import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message, CallbackQuery
from create_bot import bot, bot_username
from db_handlers.db import insert_user, get_user_data, get_user_jobs
from keyboards.kbs import main_kb
from aiogram.utils.chat_action import ChatActionSender
from create_bot import AsyncSessionLocal

user_router = Router()


@user_router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        user_info = await get_user_data(user_id=message.from_user.id)

    if user_info:
        schedule_status = "ON" if user_info.get("schedule_on") else "OFF"
        response_text = f'{user_info.get("username")}, hello there!\nYour default schedule time is {user_info.get("schedule_time")}\nYour schedule now is {schedule_status}'
        if user_info.get("job_name") is not None:
            response_text += f'\nYour current job name is {user_info.get("job_name")}'
        else:
            response_text += '\nYou don\'t have any job for searching yet.'
    else:
        await insert_user(user_data={
            'id': message.from_user.id,
            'username': message.from_user.username,
        })
        response_text = (f'{message.from_user.username}, Welcome to bot.\n')
    await message.answer(text=response_text, reply_markup=main_kb(message.from_user.id))


@user_router.message(F.text.contains('My jobs'))
async def my_jobs_handler(message: Message):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        user_info = await get_user_data(user_id=message.from_user.id)
        jobs = await get_user_jobs(user_id=user_info['user_id'])
        if not jobs:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You don't have any jobs yet."
            )
            return

        jobs_text = "\n\n".join(
            [
                f"📋 <b>{job.title}</b>\n"
                f"🏢 Company: {job.company}\n"
                f"📍 Location: {job.location}\n"
                f"💵 Salary: {job.salary}\n"
                f"🔗 Link: {job.link}"
                for job in jobs
            ]
        )

        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Your jobs:\n\n{jobs_text}",
            parse_mode="HTML"
        )



async def send_jobs_page(chat_id, jobs, page):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    jobs_on_page = jobs[start:end]

    jobs_text = "\n\n".join(
        [
            f"📋 <b>{job.title}</b>\n"
            f"🏢 Company: {job.company}\n"
            f"📍 Location: {job.location}\n"
            f"💵 Salary: {job.salary}\n"
            f"🔗 Link: {job.link}"
            for job in jobs_on_page
        ]
    )

    total_pages = (len(jobs) + PAGE_SIZE - 1) // PAGE_SIZE
    keyboard = InlineKeyboardMarkup(row_width=2)
    if page > 0:
        keyboard.insert(InlineKeyboardButton("⬅️ Back", callback_data=f"jobs_page:{page-1}"))
    if page < total_pages - 1:
        keyboard.insert(InlineKeyboardButton("➡️ Next", callback_data=f"jobs_page:{page+1}"))

    await bot.send_message(
        chat_id=chat_id,
        text=f"Your jobs (page {page + 1} / {total_pages}):\n\n{jobs_text}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@user_router.callback_query(F.data.startswith('jobs_page:'))
async def jobs_page_callback_handler(callback_query: CallbackQuery):
    _, page = callback_query.data.split(':')
    page = int(page)

    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback_query.from_user.id)
        if not user or not user.jobs:
            await callback_query.message.edit_text("You don't have any jobs yet.")
            return

        await send_jobs_page(callback_query.from_user.id, user.jobs, page)
        await callback_query.answer()

