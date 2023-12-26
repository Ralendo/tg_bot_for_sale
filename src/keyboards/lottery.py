from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.config import Config
from src.calculations.words import return_declension_of_product_name


def lottery_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Участвую!', callback_data='lottery_join'))
    return keyboard