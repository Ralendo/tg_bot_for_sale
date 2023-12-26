import aiogram.utils.exceptions
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from src.services import User_Switch
from src.bot import dp, db
from src.keyboards import basket_keyboard
import src.calculations.words as word

# Передаётся product_name для конкретного товара в корзине.
# Из FSM: basket - корзина, являющийся двумерным массивом, где строки = товар,
# в которых первый столбец это название товара, а второй столбец - количество товара


# Плюс один товар
@dp.callback_query_handler(lambda c: c.data.startswith('num_inc'), state=User_Switch.input_off)
async def plus(call: CallbackQuery, state: FSMContext):
    _, product_name = call.data.split("|")
    async with state.proxy() as data:
        basket = data['basket']

    index = None
    for i in basket:
        if i[0] == product_name:
            index = basket.index(i)
            break

    count_in_stock = await db.get_count_in_stock(product_name)
    price_ticket = await db.get_price_in_stock(product_name)

    if count_in_stock == 0:
        await call.answer('Все билеты распроданы :(')
        return 0
    elif basket[index][1] < count_in_stock:
        basket[index][1] += 1
        total_price = (basket[index][1]) * price_ticket
        async with state.proxy() as data:
            data['basket'] = basket

        await call.message.edit_text(f'- Сколько билетов ты хочешь купить?'
                                     f'\n- Я хочу купить <b>{word.update_word_total(basket[index])}</b>'
                                     f'\n- Хорошо, тебе это обойдётся в <b>{total_price} ₽</b>'
                                     f'\nЧтобы вернуться в магазин, нажми кнопку "Назад в Магазин".',
                                     reply_markup=basket_keyboard(product_name))
    else:
        await call.answer('Больше нет в наличии :(')
        return 0


# Минус один товар
@dp.callback_query_handler(lambda c: c.data.startswith('num_decr'), state=User_Switch.input_off)
async def minus(call: CallbackQuery, state: FSMContext):
    _, product_name = call.data.split("|")
    async with state.proxy() as data:
        basket = data['basket']

    index = None
    for i in basket:
        if i[0] == product_name:
            index = basket.index(i)
            break

    price_ticket = await db.get_price_in_stock(product_name)
    if basket[index][1] == 1:
        basket[index][1] = 0
        async with state.proxy() as data:
            data['basket'] = basket

        await call.message.edit_text(f'- Сколько билетов ты хочешь купить?\n- Я хочу купить ...',
                                     reply_markup=basket_keyboard(product_name))
    elif not basket[index][1] or basket[index][1] == 0:
        await call.answer('Товар в  корзине отсутствует!')
        return 0
    else:
        basket[index][1] -= 1
        total_price = basket[index][1] * price_ticket
        async with state.proxy() as data:
            data['basket'] = basket

        await call.message.edit_text(f'- Сколько билетов ты хочешь купить?'
                                     f'\n- Я хочу купить <b>{word.update_word_total(basket[index])}</b>'
                                     f'\n- Хорошо, тебе это обойдётся в <b>{total_price} ₽</b>'
                                     f'\nЧтобы вернуться в магазин, нажми кнопку "Назад в Магазин".',
                                     reply_markup=basket_keyboard(product_name))


# Обнулить корзину
@dp.callback_query_handler(lambda c: c.data.startswith('btn_clear'), state=User_Switch.input_off)
async def cart_equal_zero(call: CallbackQuery, state: FSMContext):
    _, product_name = call.data.split("|")
    async with state.proxy() as data:
        basket = data['basket']

    for i in basket:
        if i[0] == product_name:
            i[1] = 0
            break
    async with state.proxy() as data:
        data['basket'] = basket

    try:
        await call.answer('Корзина обнулена')
        await call.message.edit_text(f'- Сколько билетов ты хочешь купить?\n- Я хочу купить ...',
                                     reply_markup=basket_keyboard(product_name))
    except aiogram.utils.exceptions.MessageNotModified:
        await call.answer('Корзина обнулена')
