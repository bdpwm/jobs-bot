from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
from datetime import datetime
from aiogram import Bot
from aiogram.types import Message

from create_bot import bot, scheduler
from db_handlers.db import get_users_with_schedule

async def job_parsing_and_sending():
    users = await get_users_with_schedule()
    current_hour = datetime.now().hour

    for user in users:
        if user.schedule_time == current_hour:
            jobs = await parse_jobs_for_user(user.job_name)

            await send_jobs_to_user(user, jobs)



# !!! rework DRY !!!
async def send_jobs_to_user(user, jobs):
    if not jobs:
        await bot.send_message(user.user_id, "No jobs found for your search.")
        return

    jobs_text = "\n\n".join(
        [
            f"📋 <b>{job.title}</b>\n"
            f"🏢 Company: {job.company}\n"
            f"📍 Location: {job.location}\n"
            f"💵 Salary: {job.salary}\n"
            f"🔗 <a href='https://www.work.ua{job.link}'>Click</a>"
            for job in jobs
        ]
    )

    await bot.send_message(
        user.user_id,
        f"Your jobs:\n\n{jobs_text}",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def parse_jobs_for_user(job_name: str):
    return await fetch_job_work_ua(job_name)


scheduler.add_job(job_parsing_and_sending, CronTrigger(minute=00))

