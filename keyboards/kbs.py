from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_kb(user_telegram_id: int):
    kb_list = [[KeyboardButton(text="Info")], [KeyboardButton(text="Find a Job")], [KeyboardButton(text="Time to scheduler")], [KeyboardButton(text="ON/OFF")]]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="JOBS-BOT"
    )