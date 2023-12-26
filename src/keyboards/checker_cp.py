from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_info_checker():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Понял!', callback_data='start_info_checker'))
    return keyboard


def check_keyboard(name):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Пришёл', callback_data=f'human_arrived|{name}'))
    keyboard.add(InlineKeyboardButton(text='Не пришёл', callback_data=f'human_not_arrived|{name}'))
    return keyboard