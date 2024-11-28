import asyncio
from create_bot import bot, dp, scheduler, init_db, drop_db
from handlers.user_router import user_router
from handlers.jobs_router import jobs_router


async def main():
    # await drop_db()
    await init_db()

    dp.include_router(jobs_router)
    dp.include_router(user_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())