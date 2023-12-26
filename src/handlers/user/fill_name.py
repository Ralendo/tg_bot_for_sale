from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext

from src.services import User_Switch, generate_qrcode
from src.bot import dp, bot, db, logger
from src.keyboards import accept_keyboard, back_to_menu
from src.messages import fill_message
from src.config import Config
from src.calculations.words import return_declension_of_product_name


@dp.callback_query_handler(text='fill_go', state=User_Switch.input_off)
async def start_fill(call: CallbackQuery, state: FSMContext):
    try:
        label = await db.get_last_label_from_buyers(call.from_user.id)
        count_of_products = await db.get_count_types_of_products(label)
        product_name = await db.get_product_name_first(label)
        ticket_id = await db.get_ticket_id(label, product_name)

        if count_of_products > 1:
            name = return_declension_of_product_name(product_name)
            if name == 'Обычный':
                name = 'обычных'
            text = f'- Поскольку ты купил несколько типов билетов, то мы начнём с {name} билетов. Введи имя человека...'
        else:
            text = fill_message["filling_name"]

        async with state.proxy() as data:
            data['product_name'] = product_name
            data['label'] = label
            data['ticket_id'] = ticket_id

        await call.message.edit_text(text)
    except Exception as e:
        logger.exception(e)
    await User_Switch.input_on.set()

# Кнопка проверки
@dp.message_handler(state=User_Switch.input_on)
async def accept_fill(message: Message, state: FSMContext):
    name = message.text
    async with state.proxy() as data:
        data['name'] = name
    await bot.send_message(message.chat.id, f'- Я правильно запомнил?\n {name} ',
                           reply_markup=accept_keyboard())


# Кнопка подтверждения
@dp.callback_query_handler(text='accept_name', state=User_Switch.input_on)
async def add_names_to_buyers(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        name = data['name']
        product_name = data['product_name']
        ticket_id = data['ticket_id']
        label = data['label']

    await call.message.edit_text(call.message.text)

    # Добавляем имя в таблицу ticket_names в столбец имён
    if product_name == 'VIP':
        name = 'VIP: ' + name
    await db.add_ticket_name(ticket_id, name)

    count = await db.get_count_from_tickets(product_name, label)
    count -= 1
    await db.update_count_in_buyers(count, product_name, label)
    if count > 0:
        await bot.send_message(call.message.chat.id, fill_message["next_name"])
    elif count == 0:
        # Если все добавлены, то проверяем, есть ли ещё незаполненные билеты на эту транзакцию.
        count_of_products = await db.get_count_types_of_products(label)
        if count_of_products > 0:
            product_name = await db.get_product_name_first(label)
            name = return_declension_of_product_name(product_name)
            if name == 'Обычный':
                name = 'обычные'
            text = f'- Мы закончили с заполнением этого типа билетов. Теперь начнём заполнять {name} билеты!' \
                   f'\nВводи имя следующего человека...'
            async with state.proxy() as data:
                data['product_name'] = product_name
            await call.message.edit_text(text)
        else:
            # Если билетов на заполнение нет, то отправляем message со списком имён и QR-кодом, и выключаем приём ввода

            img = generate_qrcode(label)

            output_names = ''
            list_names = await db.get_ticket_names(label)
            for row in list_names:
                output_names += '\n' + str(row)
            msg = await bot.send_photo(call.message.chat.id, img,
                                       caption=f"{fill_message['final_fill']} {output_names}",
                                       reply_markup=back_to_menu())

            # Получение id photo на хранение
            photo_id = msg['photo'][-1]['file_id']
            await db.update_photo_id(photo_id, label)

            # Log заполнения билетов
            try:
                logger.info(f'Пользователь {call.from_user.id} под ником {call.from_user.username} получил свои билеты!')
            except OSError:
                pass
            # Выключаем состояния ввода и FSM
            await state.finish()
            await User_Switch.input_off.set()
    else:
        logger.exception('Что то не так во время получения билетов')
        pass


# Кнопка отмены
@dp.callback_query_handler(text='decline_name', state=User_Switch.input_on)
async def return_to_input(call: CallbackQuery):
    await call.message.edit_text(fill_message["error_name"])
