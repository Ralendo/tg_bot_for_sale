from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.config import Config
from src.calculations.words import return_declension_of_product_name


def shop_keyboard(basket, promocode):
    keyboard = InlineKeyboardMarkup(row_width=3)
    btn = []
    for name in basket:
        text = return_declension_of_product_name(name[0])
        btn.append(InlineKeyboardButton(text=text, callback_data=f'btn_shop_choice|{name[0]}'))

    keyboard.row(*btn)
    if not promocode:
        keyboard.add(InlineKeyboardButton(text='У меня промокод!', callback_data='btn_promocode'))
    keyboard.add(InlineKeyboardButton(text='Оплатить', callback_data='btn_buy'))

    return keyboard
