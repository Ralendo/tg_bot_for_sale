from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def basket_keyboard(product_name):
    buttons = [
        InlineKeyboardButton(text='+', callback_data=f'num_inc|{product_name}'),
        InlineKeyboardButton(text='-', callback_data=f'num_decr|{product_name}'),
        InlineKeyboardButton(text='Обнулить', callback_data=f'btn_clear|{product_name}'),
        InlineKeyboardButton(text='Назад в Магазин', callback_data=f'shop_back')
    ]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(*buttons)
    return keyboard
