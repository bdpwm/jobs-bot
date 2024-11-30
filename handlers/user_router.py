import asyncio

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender

from create_bot import AsyncSessionLocal, bot, bot_username
from db_handlers.db import get_user_data, get_user_jobs, insert_user
from keyboards.kbs import main_kb

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
                f"💵 Salary: {job.salary}\n"
                f"🔗 <a href='https://www.work.ua{job.link}'>Click</a>"
                for job in jobs
            ]
        )

        await bot.send_message(chat_id=message.from_user.id, text=f"Your jobs parsed before:\n\n{jobs_text}", parse_mode="HTML", disable_web_page_preview=True,)

