import asyncio
from datetime import datetime
from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from create_bot import bot, scheduler
from db_handlers.db import delete_jobs_for_user, get_user_jobs, get_users_with_schedule
from utils.utils import fetch_job_work_ua


async def job_parsing_and_sending():
    users = await get_users_with_schedule()
    current_hour = datetime.now().hour
    
    for user in users:
        user_hour = user.schedule_time.hour
        if user_hour == current_hour:
            await delete_jobs_for_user(user_id=user.user_id)
            await parse_jobs_for_user(user_id=user.user_id, job_name=user.job_name)
            await send_jobs_to_user(user=user)


async def send_jobs_to_user(user):
    jobs = await get_user_jobs(user_id=user.user_id)
    if not jobs:
        await bot.send_message(user.user_id, "No jobs found for your search.")
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

    today_date = datetime.now().strftime("%Y-%m-%d")
    await bot.send_message(user.user_id, f"Your jobs for {today_date}:\n\n{jobs_text}", parse_mode="HTML", disable_web_page_preview=True)

async def parse_jobs_for_user(user_id: int, job_name: str):
    await fetch_job_work_ua(job_name, user_id)

scheduler.add_job(job_parsing_and_sending, CronTrigger(minute=00))

