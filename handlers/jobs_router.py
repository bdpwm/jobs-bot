import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from create_bot import bot, bot_username
from db_handlers.db import insert_user, get_user_data, update_on_off_schedule, save_selected_hour, save_job_name
from keyboards.kbs import main_kb
from aiogram.utils.chat_action import ChatActionSender

jobs_router = Router()

@jobs_router.message(F.text.contains('ON/OFF'))
async def on_off_handler(message: Message):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        user_info = await get_user_data(user_id=message.from_user.id)


        if user_info.get("schedule_on") == True:
            await update_on_off_schedule(user_id=message.from_user.id, schedule_on=False)
            await message.answer(text="Your schedule is OFF now.")
        else:
            await update_on_off_schedule(user_id=message.from_user.id, schedule_on=True)
            await message.answer(text="Your schedule is ON now.")

@jobs_router.message(F.text.contains("Time to scheduler"))
async def time_to_scheduler_handler(message: Message):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for hour in range(0, 24):
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=f"{hour:02d}:00", callback_data=f"hour_{hour}")]
            )
        await message.answer("Select time:", reply_markup=keyboard)


@jobs_router.callback_query(F.data.startswith("hour_"))
async def select_hour(call: CallbackQuery):
    hour = int(call.data.split("_")[1])
    selected_time = f"{hour:02d}:00"
    await call.message.edit_text(f"Schedule time set to: {selected_time}")
    await save_selected_hour(user_id=call.from_user.id, selected_hour=hour)

@jobs_router.message(F.text.contains("Find a Job"))
async def find_a_job_handler(message: Message):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        await message.answer("Give a job name, for example - Junior Python Developer")

        @jobs_router.message(F.text)
        async def save_job_name_handler(response_message: Message):
            if response_message.from_user.id == message.from_user.id:
                job_name = response_message.text
                await save_job_name(user_id=message.from_user.id, job_name=job_name)
                await response_message.answer(f"Job name '{job_name}' saved successfully!")