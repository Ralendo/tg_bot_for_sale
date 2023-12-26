from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from src.messages import transaction_message
from src.bot import bot, dp, db, logger
from src.services import User_Switch, yoomoney_create_url
from src.keyboards import back_to_menu, transaction, go_fill_names, back_to_shop

from yoomoney import Client
from src.config import Config
import time

import src.calculations.basket as calculation
import src.calculations.words as word
import src.calculations.payment_success as payment_success


# Кнопка покупки
@dp.callback_query_handler(text='btn_buy', state=User_Switch.input_off)
async def p2p_buy(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        basket = data['basket']
        promocode = data['promocode']

    # Проверка, что корзина не пустая
    if not calculation.basket_check_null(basket):
        msg = '- Ну нельзя же купить пустоту, не так ли? Давай вернёмся в Магазин и попробуем ещё раз?'
        await call.message.edit_text(msg, reply_markup=back_to_shop())
    else:
        logger.info(f'Пользователь {call.from_user.id} под ником {call.from_user.username} хочет что-то купить!\n{basket}')

        try:
            total_price = await calculation.total_basket(basket, db)

            discount = 0
            if promocode:
                discount = await db.get_discount(promocode)
                total_price -= discount

            text = '- Так, давай-ка посмотрим что тут у нас...'
            pull_price = []
            for row in basket:
                price = await db.get_price_in_stock(row[0]) * row[1]
                pull_price.append(price)
            text += word.basket_content(basket, discount, pull_price)
            text += f'\nИтого получается: <b>{total_price} ₽</b>.'

            msg = f'\nНажми кнопку "Оплатить",чтобы перейти к оплате. После совершения оплаты, нажми кнопку "Подтвердить"'
            text += msg

            label = None
            check = True
            while check:
                label = word.create_label()
                check = await db.check_exist_label_in_table(label)

            url = yoomoney_create_url(total_price, label)

            async with state.proxy() as data:
                data['label'] = label

            await call.message.edit_text(text, reply_markup=transaction(url))
        except Exception as e:
            logger.exception(e)


@dp.callback_query_handler(text='get_payment', state=User_Switch.input_off)
async def check_payment(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        label = data['label']
        promocode = data['promocode']
        basket = data['basket']
        referral = ': #' + data['referral'] if 'referral' in data.keys() and data['referral'] else 'отсутствует'

    try:
        client = Client(Config.token_p2p)
        history = client.operation_history(label=label)
        operation = history.operations[-1]
        if operation.status == 'success':
        # check = True
        # if check:
            try:
                logger.info(f" Пользователь {call.from_user.id} под именем {call.from_user.username}"
                            f" купил {basket}")
                total_basket = int(basket[0][1])
                if basket[1][1] > 0:
                    total_basket += int(basket[1][1])
                spam_text = (f"ID: {call.from_user.id}\n "
                             f"Имя: {call.from_user.first_name}\n"
                             f"Фамилия: {call.from_user.last_name}\n"
                             f"Никнейм: {call.from_user.username}\n"
                             f"Купил {total_basket} билетов\n"
                             f"Заплатил: {operation.amount}\n"
                             f"UTM-метка: {referral}")

                for user in Config.access_users:
                    await bot.send_message(chat_id=user, text=spam_text)
            except Exception as e:
                logger.exception(e)
                pass

            # Вычитаем из склада купленные билеты
            await payment_success.bought_tickets(basket, db)

            # Делаем использованность промокода
            if promocode:
                await db.use_promocode(promocode)

            # Добавляем клиента в БД и передаём количество купленных (=не распределённых) билетов
            await db.add_user_to_buyers(call.from_user.id, label, operation.amount)
            await db.add_ticket(basket, label)

            # Переход к заполнению билетов
            await call.answer(transaction_message['successful_payment'], show_alert=True)

            text = '- Умничка!' \
                   '\nОсталось последнее: Давай заполним билеты?'
            await call.message.edit_text(text=text, reply_markup=go_fill_names())

        else:
            await call.answer(transaction_message['wait_msg'], show_alert=True)

    except IndexError:
        await call.answer(transaction_message['wait_msg'], show_alert= True)

    except Exception as e:
        logger.exception(e)
        await call.answer(transaction_message['wait_msg'], show_alert=True)



# for operation in history.operations:
    #     print()
    #     print("Operation:", operation.operation_id)
    #     print("\tStatus     -->", operation.status)
    #     print("\tDatetime   -->", operation.datetime)
    #     print("\tTitle      -->", operation.title)
    #     print("\tPattern id -->", operation.pattern_id)
    #     print("\tDirection  -->", operation.direction)
    #     print("\tAmount     -->", operation.amount)
    #     print("\tLabel      -->", operation.label)
    #     print("\tType       -->", operation.type)
