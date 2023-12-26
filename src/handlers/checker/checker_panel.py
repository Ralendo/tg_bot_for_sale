from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from src.services import Checker_Switch
from src.bot import dp, bot, db, logger
from src.keyboards import check_keyboard, start_info_checker
from src.messages import info_message


# Инфа для проверяющего
async def checker_info(message):
    await bot.send_message(message.chat.id, info_message['info_checker'], reply_markup=start_info_checker())


# Стартовое сообщение для проверяющего
@dp.callback_query_handler(text='start_info_checker', state=Checker_Switch.input_off)
async def start_checker_work(call: CallbackQuery, state: FSMContext):
    await Checker_Switch.input_on.set()
    await bot.edit_message_text('Хорошо, тогда введи код билета..', call.from_user.id, call.message.message_id)
    async with state.proxy() as data:
        data['counter_people'] = 1

# Пришёл человек
@dp.callback_query_handler(lambda c: c.data.startswith('human_arrived'), state=Checker_Switch.input_on)
async def checker_ticket_accept(call: CallbackQuery, state: FSMContext):
    try:
        _, name = call.data.split("|")
        async with state.proxy() as data:
            label = data['label']
            counter_people = data['counter_people']

        await db.update_ticket_name_check(label, name)
        logger.info(f"№{counter_people}: '{name}' пришёл на тусу под билетом № {label}!")
        text = f"№{counter_people}: {name} прошёл!"
        await bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        async with state.proxy() as data:
            data['counter_people'] = counter_people + 1
    except Exception as e:
        logger.exception(e)


# Не пришёл человек
@dp.callback_query_handler(lambda c: c.data.startswith('human_not_arrived'), state=Checker_Switch.input_on)
async def checker_ticket_decline(call: CallbackQuery, state: FSMContext):
    try:
        _, name = call.data.split("|")
        async with state.proxy() as data:
            label = data['label']

        text = f"{name} не пришёл!"
        await bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        logger.info(f"'{name}' НЕ ПРИШЁЛ на тусу под билетом № {label}!")
    except Exception as e:
        logger.exception(e)


# Ловим номер билета
@dp.message_handler(state=Checker_Switch.input_on)
async def check_ticket(message: Message, state: FSMContext):
    label = message.text
    try:
        check = await db.check_exist_ticket(label)
        if check:
            names = await db.get_ticket_names_for_checker(label)
            if names:
                for name in names:
                    async with state.proxy() as data:
                        data['label'] = label
                    await bot.send_message(chat_id=message.chat.id, text=name, reply_markup=check_keyboard(name))
                text = 'По данному билету все проверены!' \
                       '\nВводи следующий номер билета.'
                await bot.send_message(text=text, chat_id=message.chat.id)
            else:
                await message.answer('По данному билету все прошли!')
        else:
            await message.answer('Такого билета нет!')
    except Exception as e:
        logger.exception(e)
        await message.answer('Что-то пошло не так, требуется помощь.')
