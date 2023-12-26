from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_to_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Вернуться в Главное меню', callback_data='main_menu'))
    return keyboard

def back_to_shop():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Вернуться в Магазин', callback_data='shop_back'))
    return keyboard




