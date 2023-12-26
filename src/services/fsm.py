from aiogram.dispatcher.filters.state import StatesGroup, State


class User_Switch(StatesGroup):
    input_on = State()
    input_off = State()
    input_promocode = State()

class Checker_Switch(StatesGroup):
    input_on = State()
    input_off = State()

class Admin_Switch(StatesGroup):
    input_new_count = State()
    input_new_price = State()
    input_new_role = State()
    input_new_promocodes = State()
    input_off = State()
