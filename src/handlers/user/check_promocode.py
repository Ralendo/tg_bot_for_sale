from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from aiogram.utils.exceptions import MessageNotModified

from src.bot import bot, dp, db, logger
from src.services import User_Switch
from src.keyboards import back_to_shop
from src.handlers.user.shop import shop_back
from src.handlers.user.fill_name import start_fill

import src.calculations.words as word


# Сообщение с просьбой ввести промокод
@dp.callback_query_handler(text='btn_promocode', state=User_Switch.input_off)
async def input_promocode_message(call: CallbackQuery, state: FSMContext):
    await User_Switch.input_promocode.set()
    text = '- Хорошо, тогда введи его..'

    async with state.proxy() as data:
        data['call'] = call
        data['text'] = text
        data['msg_from_bot'] = None

    await bot.edit_message_text(text, call.message.chat.id, call.message.message_id)


# Кнопка проверки
@dp.message_handler(state=User_Switch.input_promocode)
async def promocode_message(message: Message, state: FSMContext):
    async with state.proxy() as data:
        call = data['call']
        text = data['text']
        msg = data['msg_from_bot']
    try:
        if msg:
            message_chat_id = msg['chat']['id']
            message_message_id = msg['message_id']
            await bot.edit_message_text(text[:77], message_chat_id, message_message_id)
    except MessageNotModified:
            pass
    except Exception as e:
        logger.exception(e)
    promocode = message.text
    check = await db.check_exists_promocode(promocode)
    if check == 'ok':
        async with state.proxy() as data:
            data['promocode'] = promocode
        await User_Switch.input_off.set()
        await shop_back(call, state)
        logger.info(
            f'Пользователь {message.from_user.id} активировал промокод {promocode} !')
        await call.answer('Промокод активирован!')
    elif check == 'service':
        count = await db.get_service_count(promocode)
        basket = [['1Ticket', count]]
        label = word.create_free_label(int(message.from_user.id/1000))
        # Добавляем клиента в БД и передаём количество купленных (=не распределённых) билетов
        await db.add_user_to_buyers(message.from_user.id, label, 0)
        await db.add_ticket(basket, label)

        await db.use_promocode(promocode)
        await User_Switch.input_off.set()
        logger.info(f'Пользователь {message.from_user.id} активировал сервисный промокод {promocode} на {count} человек!')
        await call.answer('Сервисный промокод активирован!')
        await start_fill(call, state)
    else:
        text = f'- Я у себя проверил, но такого промокода у меня нет.'\
               f'\nЛибо он уже активирован.' \
               f'\nНапиши его ещё раз, или можешь вернуться в Главное меню'
        msg = await bot.send_message(message.chat.id, text, reply_markup=back_to_shop(),
                                     reply_to_message_id=message.message_id)
        async with state.proxy() as data:
            data['text'] = text
            data['msg_from_bot'] = msg
