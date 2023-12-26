from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Магазин', callback_data='shop'))
    keyboard.add(InlineKeyboardButton(text='Показать билет', callback_data='get_ticket'))
    return keyboard
