from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, insert
from create_bot import AsyncSessionLocal
from sqlalchemy.exc import NoResultFound
from db_handlers.models import User, Job
from datetime import date, timedelta, time
from sqlalchemy.dialects.postgresql import insert


async def insert_user(user_data: dict):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            schedule_time = time(9, 0)
            stmt = insert(User).values(
                user_id=user_data['id'],
                username=user_data['username'],
                job_name=user_data.get('job_name', None),
                schedule_time=schedule_time,
                schedule_on=True
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_id'],
                set_={
                    'username': user_data['username'],
                    'job_name': user_data.get('job_name', None),
                    'schedule_time': schedule_time,
                    'schedule_on': True
                }
            )
            await session.execute(stmt)


async def get_user_data(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            return {
                "user_id": user.user_id,
                "username": user.username,
                "job_name": user.job_name,
                "schedule_time": user.schedule_time,
                "schedule_on": user.schedule_on,
            }
    return None

async def update_on_off_schedule(user_id: int, schedule_on: bool):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(User).where(User.user_id == user_id).values(schedule_on=schedule_on)
        )
        await session.commit()

async def save_selected_hour(user_id: int, selected_hour: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(User).where(User.user_id == user_id).values(schedule_time=time(selected_hour, 0))
        )
        await session.commit()

async def save_job_name(user_id: int, job_name: str):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(User).where(User.user_id == user_id).values(job_name=job_name)
        )
        await session.commit()


async def get_user_jobs(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Job).where(Job.user_id == user_id)
        )
        return result.scalars().all()

async def save_job(job_data, user_id):
    async with AsyncSessionLocal() as session:
        job_id = int(job_data["link"].split("/")[-2])

        job = Job(
            id=job_id,
            title=job_data["title"],
            job_from=job_data["job_from"],
            salary=job_data["salary"],
            company=job_data["company"],
            location=job_data["location"],
            user_id=user_id,
            link=job_data["link"]
        )
        session.add(job)
        await session.commit()



async def get_users_with_schedule():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter(User.schedule_on == True))
        return result.scalars().all()