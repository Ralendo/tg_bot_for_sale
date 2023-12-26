from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.web_app_info import WebAppInfo

def transaction(url):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Оплатить', web_app=WebAppInfo(url=url)))
    keyboard.add(InlineKeyboardButton(text='Подтвердить платёж', callback_data='get_payment'))
    return keyboard

def go_fill_names():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Давай!', callback_data='fill_go'))
    return keyboard
