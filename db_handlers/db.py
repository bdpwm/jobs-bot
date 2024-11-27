from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, insert
from create_bot import AsyncSessionLocal
from sqlalchemy.exc import NoResultFound
from db_handlers.models import User
from datetime import date, timedelta
from sqlalchemy.dialects.postgresql import insert


async def insert_user(user_data: dict):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = insert(User).values(
                user_id=user_data['id'],
                username=user_data['username'],
                job_name=user_data.get('job_name', None),
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_id'],
                set_={
                    'username': user_data['username'],
                    'job_name': user_data.get('job_name', None),
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
            }
    return None
