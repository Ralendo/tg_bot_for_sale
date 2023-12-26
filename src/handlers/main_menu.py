from aiogram.types import Message, CallbackQuery, InputFile
from sqlalchemy.exc import OperationalError

import time

from src.messages import info_message, fill_message, transaction_message
from src.bot import bot, dp, db, logger
from src.services import User_Switch, Admin_Switch, Checker_Switch
from src.keyboards import start_keyboard, back_to_menu, continue_fill_name_keyboard
from src.config import Config

from src.handlers.admin.admin_panel import admin_info
from src.handlers.checker.checker_panel import checker_info

from aiogram.dispatcher.storage import FSMContext

# cmd /start
@dp.message_handler(commands='start', state="*")
async def cmd_start(message: Message, state: FSMContext) -> None:
    try:
        user = message.from_user

        # Использование: t.me/<bot_username>?start=<parameter>
        # <parameter> ограничен 64 символами base64url со стороны Телеграма
        referral = message.get_args()
        await state.update_data(referral=referral)

        logger.debug(f"Пользователь '{user.id}' "\
                     f"под именем '{user.username}' воспользовался ботом! "\
                     f"{'Utm: ' + referral if referral else ''}")

        try:
            check = await db.exist_user(user.id)
        except OperationalError:
            time.sleep(0.5)
            check = await db.exist_user(user.id)
        if not check:
            await db.add_users(user.id, user.first_name, user.last_name, user.username)

        role = await db.get_permission_status(user.id)
        # Условие проверки в ЧС, если нет, то перебираем роль для перенаправления в нужный интерфейс.
        if user.id == 888888:
            await bot.send_message(message.chat.id, 'Извините, но вы находитесь в чёрном списке!')
        else:
            if role == 'admin':
                await Admin_Switch.input_off.set()
                await admin_info(message)
            elif role == 'checker':
                await Checker_Switch.input_off.set()
                await checker_info(message)
            else:
                if (not Config.app_access) and (user.id != Config.admin_id):
                    await bot.send_message(message.chat.id,
                                           'У нас технические работы, но в скором времени мы вернёмся!')
                else:
                    await bot.delete_message(user.id, message.message_id)
                    await User_Switch.input_off.set()
                    # Если человек не заполнил билет, то предлагаем продолжить заполнение
                    check = await db.check_exist_non_distributed_tickets(user.id)
                    if check:
                        await bot.send_message(message.chat.id,
                                               '- Слушай, видимо ты не заполнил именами билеты. Давай продолжим?',
                                               reply_markup=continue_fill_name_keyboard())
                    else:
                        photo = InputFile(Config.file_path_afisha)
                        await bot.send_photo(chat_id=message.chat.id, photo=photo,
                                             caption=info_message['start'], reply_markup=start_keyboard())
    except Exception as e:
        logger.exception(e)


# Главное меню как обработка callback (Для Юзеров)
@dp.callback_query_handler(text='main_menu', state="*")
async def main_menu(call: CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await User_Switch.input_off.set()
    photo = InputFile(Config.file_path_afisha)
    await bot.send_photo(chat_id=call.from_user.id, photo=photo,
                         caption=info_message['start'], reply_markup=start_keyboard())


# Получение билета, если он уже куплен
@dp.callback_query_handler(text="get_ticket", state=User_Switch.input_off)
async def get_ticket(call: CallbackQuery):
    data = await db.get_labels_from_buyers(call.message.chat.id)
    try:
        if data:
            await bot.delete_message(call.from_user.id, call.message.message_id)
            for label in data:
                photo_id = await db.get_photo_id(label)

                output_names = ''
                names = await db.get_ticket_names(label)
                for name in names:
                    output_names += '\n' + str(name)

                kb = None
                if label == data[-1]:
                    kb = back_to_menu()

                await bot.send_photo(call.from_user.id, photo_id,
                                     caption=f"{fill_message['ticket_fill']} {output_names}",
                                     reply_markup=kb)
        else:
            await call.answer(transaction_message['wait_msg'], show_alert=True)
    except Exception as e:
        logger.exception(e)
        await call.answer(transaction_message['wait_msg'], show_alert=True)
