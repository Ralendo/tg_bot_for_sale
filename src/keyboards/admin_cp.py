from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.config import Config
from src.calculations.words import return_declension_of_product_name


def admin_mainmenu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Билеты', callback_data='admin_tickets'))
    keyboard.add(InlineKeyboardButton(text='Роли', callback_data='admin_roles'))
    keyboard.add(InlineKeyboardButton(text='Промокоды', callback_data='admin_promocodes'))
    return keyboard


def admin_choice_tickets(names):
    keyboard = InlineKeyboardMarkup()
    for name in names:
        keyboard.add(InlineKeyboardButton(text=f'{return_declension_of_product_name(name)}', callback_data=f'admin_edit_tickets|{name}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='admin_mainmenu'))
    return keyboard


def admin_edit_tickets():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Изменить цену', callback_data='admin_ticket_edit_price'))
    keyboard.add(InlineKeyboardButton(text='Изменить количество', callback_data='admin_ticket_edit_count'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='admin_mainmenu'))
    return keyboard

def admin_edit_user_role():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='-> User', callback_data='admin_edit_role|user'))
    keyboard.add(InlineKeyboardButton(text='-> Checker', callback_data='admin_edit_role|checker'))
    keyboard.add(InlineKeyboardButton(text='-> Admin', callback_data='admin_edit_role|admin'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='admin_mainmenu'))
    return keyboard

def admin_promocode_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Да', callback_data='admin_addpromocodes'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='admin_mainmenu'))
    return keyboard
