import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from create_bot import bot, bot_username
from db_handlers.db import insert_user, get_user_data, update_on_off_schedule, save_selected_hour_to_db
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

@jobs_router.message(F.text == "Time to scheduler")
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
    await save_selected_hour_to_db(user_id=call.from_user.id, selected_hour=hour)