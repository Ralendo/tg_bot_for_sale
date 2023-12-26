from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from src.services import User_Switch
from src.bot import dp, bot, db, logger
from src.keyboards import shop_keyboard, basket_keyboard

import src.calculations.words as word

# Стартовое сообщение магазина
@dp.callback_query_handler(text='shop', state=User_Switch.input_off)
async def shop(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    try:
        text = f'- Какой тип билетов ты хочешь купить?'
        product_name = await db.get_names_of_product()
        promocode = None
        basket = []
        for name in product_name:
            basket.append([name, 0])
        async with state.proxy() as data:
            data['basket'] = basket
            data['promocode'] = promocode
            data['call'] = None
            data['msg_from_bot'] = None

        keyboard = shop_keyboard(basket, promocode)
        await bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=keyboard)
    except Exception as e:
        logger.exception(e)

# Магазин mainmenu как кнопка "Назад"
@dp.callback_query_handler(text='shop_back', state='*')
async def shop_back(call: CallbackQuery, state: FSMContext):
    await User_Switch.input_off.set()
    try:
        do = 'edit'
        async with state.proxy() as data:
            try:
                basket = data['basket']
            except KeyError:
                basket = []
                product_name = await db.get_names_of_product()
                for name in product_name:
                    basket.append([name, 0])
            promocode = data['promocode']
            if data['msg_from_bot']:
                msg = data['msg_from_bot']
                do = 'send'

        text = f'- Какой тип билетов ты хочешь купить?'
        discount = 0
        if promocode:
            discount = await db.get_discount(promocode)
        pull_price = []
        for row in basket:
            price = await db.get_price_in_stock(row[0]) * row[1]
            pull_price.append(price)
        temp = word.basket_content(basket, discount, pull_price)
        text += temp
        text += '\nЧтобы перейти к оплате, нажми кнопку "Оплатить"'

        keyboard = shop_keyboard(basket, promocode)
        if do == 'edit':
            await call.message.edit_text(text, reply_markup=keyboard)
        elif do == 'send':
            temp_text = msg['text']
            await call.message.edit_text(temp_text[:77])
            await bot.send_message(call.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        logger.exception(e)


# Выбор количества билетов
@dp.callback_query_handler(lambda c: c.data.startswith('btn_shop_choice'), state=User_Switch.input_off)
async def choice_ticket(call: CallbackQuery, state: FSMContext):
    _, product_name = call.data.split('|')
    async with state.proxy() as data:
        basket = data['basket']
    index = None
    for i in basket:
        if i[0] == product_name:
            index = basket.index(i)
            break
    if basket[index][1] > 0:
        price_ticket = await db.get_price_in_stock(product_name)
        total_price = (basket[index][1]) * price_ticket
        text = f'- Сколько билетов вы хотите купить?'\
               f'\n- Я хочу купить <b>{word.update_word_total(basket[index])}</b>' \
               f'\n- Хорошо, тебе это обойдётся в <b>{total_price} ₽</b>'
    else:
        text = f'- Сколько билетов вы хотите купить?\n- Я хочу купить ...'
    await call.message.edit_text(text, reply_markup=basket_keyboard(product_name))
