from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def accept_keyboard():
    buttons = [
        InlineKeyboardButton(text='👍', callback_data='accept_name'),
        InlineKeyboardButton(text='👎', callback_data='decline_name'),
    ]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(*buttons)
    return keyboard

def continue_fill_name_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Давай!', callback_data='fill_go'))
    return keyboard

