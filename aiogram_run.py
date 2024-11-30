import asyncio

from create_bot import bot, dp, drop_db, init_db, scheduler
from handlers.jobs_router import jobs_router
from handlers.user_router import user_router
from utils.scheduler import scheduler


async def main():
    # await drop_db() # debug comment later
    await init_db()

    dp.include_router(jobs_router)
    dp.include_router(user_router)

    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())