import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message
from create_bot import bot, bot_username
from db_handlers.db import insert_user, get_user_data
from keyboards.kbs import main_kb
from aiogram.utils.chat_action import ChatActionSender
from datetime import timedelta

user_router = Router()


@user_router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        user_info = await get_user_data(user_id=message.from_user.id)

    if user_info:
        response_text = f'{user_info.get("username")}, hello there!'
    else:
        await insert_user(user_data={
            'id': message.from_user.id,
            'username': message.from_user.username,
        })
        response_text = (f'{message.from_user.username}, Welcome to bot.\n')
    await message.answer(text=response_text, reply_markup=main_kb(message.from_user.id))