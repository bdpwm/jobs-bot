import asyncio

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.chat_action import ChatActionSender

from create_bot import bot, bot_username
from db_handlers.db import (get_user_data, insert_user, save_job_name,
                            save_selected_hour, update_on_off_schedule)
from keyboards.kbs import main_kb
from utils.utils import fetch_job_work_ua


class JobStates(StatesGroup):
    waiting_for_job_name = State()

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
async def find_a_job_handler(message: Message, state: FSMContext):
    await message.answer("Give a job name, for example - Junior Python Developer")
    await state.set_state(JobStates.waiting_for_job_name)


@jobs_router.message(JobStates.waiting_for_job_name)
async def save_job_name_handler(message: Message, state: FSMContext):
    job_name = message.text
    await save_job_name(user_id=message.from_user.id, job_name=job_name)
    await message.answer(f"Job name '{job_name}' saved successfully!")
    await state.clear()