import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputFile

from src.services import Admin_Switch, generate_qrcode
from src.bot import dp, bot, db, logger
from src.keyboards import admin_mainmenu, admin_choice_tickets, admin_edit_tickets, admin_edit_user_role, admin_promocode_menu, lottery_keyboard, back_to_menu
from src.config import Config
from src.calculations.words import return_declension_of_product_name
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation

from src.messages import lottery_text, message_to_winner, lottery_final
from src.calculations.words import create_free_label

# Главное меню Админов
async def admin_info(message):
    await bot.delete_message(message.chat.id, message.message_id)
    text = 'Welcome a board, Captain. All systems online.'
    await bot.send_message(message.chat.id, text, reply_markup=admin_mainmenu())

# Главное меню Админов (в качестве Callback)
@dp.callback_query_handler(text='admin_mainmenu', state=Admin_Switch.input_off)
async def admin_info_callback(call: CallbackQuery):
    text = 'Welcome a board, Captain. All systems online.'
    await bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_mainmenu())


""""""" Панель с билетами """""""
# Главное меню билетов
@dp.callback_query_handler(text='admin_tickets', state=Admin_Switch.input_off)
async def admin_tickets_info(call: CallbackQuery):
    text = 'Раздел <b>Билеты</b>\n'
    names = await db.get_names_of_product()
    for name in names:
        current_price = await db.get_price_in_stock(name)
        current_tickets = await db.get_count_in_stock(name)
        text += f'\n{return_declension_of_product_name(name)} - осталось: {current_tickets} шт - по цене: {current_price}₽'

    await bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_choice_tickets(names))


# Действия с билетом
@dp.callback_query_handler(lambda c: c.data.startswith('admin_edit_tickets'), state=Admin_Switch.input_off)
async def admin_tickets_info(call: CallbackQuery, state: FSMContext):
    _, name = call.data.split("|")
    text = f'Выбран тип билетов <b>{return_declension_of_product_name(name)}</b>\n'
    current_price = await db.get_price_in_stock(name)
    current_tickets = await db.get_count_in_stock(name)
    text += f'\nОсталось: {current_tickets} шт' \
            f'\nЦена: {current_price}₽'
    async with state.proxy() as data:
        data['product_name'] = name

    await bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_edit_tickets())


# Кнопка ввода новой цены
@dp.callback_query_handler(text='admin_ticket_edit_price', state=Admin_Switch.input_off)
async def edit_ticket_price(call: CallbackQuery):
    await Admin_Switch.input_new_price.set()
    await bot.edit_message_text("Введите новую цену...", call.from_user.id, call.message.message_id)

@dp.message_handler(state=Admin_Switch.input_new_price)
async def input_new_price(message: Message, state: FSMContext):
    # Записываем новую цену
    async with state.proxy() as data:
        name = data['product_name']
        data['product_name'] = None
    await db.update_price_in_stock(message.text, name)
    await Admin_Switch.input_off.set()
    await admin_info(message)


# Кнопка ввода нового количества доступных билетов
@dp.callback_query_handler(text='admin_ticket_edit_count', state=Admin_Switch.input_off)
async def edit_count_tickets(call: CallbackQuery):
    await Admin_Switch.input_new_count.set()
    await bot.edit_message_text("Введите количество билетов...",  call.message.chat.id, call.message.message_id)

@dp.message_handler(state=Admin_Switch.input_new_count)
async def input_new_count_ticket(message: Message, state: FSMContext):
    # Записываем количество билетов
    async with state.proxy() as data:
        name = data['product_name']
        data['product_name'] = None
    await db.update_count_in_stock(message.text, name)
    await Admin_Switch.input_off.set()
    await admin_info(message)

""""""" *************** """""""

""""""" Панель с ролями """""""
# Главное меню с Ролями
@dp.callback_query_handler(text='admin_roles', state=Admin_Switch.input_off)
async def admin_for_role_info(call: CallbackQuery):
    text = 'Список по ролям:\n'
    names_checkers = f"<b>Проверяющие:</b> \n{await db.get_users_for_role('checker')}\n"
    names_admins = f"<b>Админов:</b> \n{await db.get_users_for_role('admin')}"
    text += names_checkers + names_admins
    await bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_edit_user_role())


# Кнопка изменения роли
@dp.callback_query_handler(lambda c: c.data.startswith('admin_edit_role'), state=Admin_Switch.input_off)
async def admin_edit_role_name(call: CallbackQuery, state: FSMContext):
    _, role = call.data.split('|')
    async with state.proxy() as data:
        data['role'] = role
    await Admin_Switch.input_new_role.set()
    await bot.edit_message_text(f"Введите user ID нового {role}'a...",  call.message.chat.id, call.message.message_id)

@dp.message_handler(state=Admin_Switch.input_new_role)
async def edit_new_role_for_user(message: Message, state: FSMContext):
    # Изменяем роль
    async with state.proxy() as data:
        role = data['role']
    await db.update_role_of_user(message.text, role)
    await Admin_Switch.input_off.set()
    await admin_info(message)

""""""" *************** """""""

""""""" Панель с промокодами """""""
# Главное меню с Промокодами
@dp.callback_query_handler(text='admin_promocodes', state=Admin_Switch.input_off)
async def admin_promocode_mainmenu(call: CallbackQuery):
    text = 'Вы хотите добавить промокоды?'
    await bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_promocode_menu())

@dp.callback_query_handler(text='admin_addpromocodes', state=Admin_Switch.input_off)
async def add_new_promocode(call: CallbackQuery):
    text = 'Хорошо, введите сумму скидки и количество промокодов для генерации. Пример: <b>50 10</b>'
    await bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
    await Admin_Switch.input_new_promocodes.set()

@dp.message_handler(state=Admin_Switch.input_new_promocodes)
async def edit_new_role_for_user(message: Message):
    text = message.text
    price, count = text.split(' ')
    price = int(price)
    count = int(count)
    await db.generate_promocodes(price, count)
    logger.info(f'Сгенерировано {count} промокодов по скидке {price} рублей')
    await Admin_Switch.input_off.set()
    await admin_info(message)

""""""" *************** """""""


@dp.message_handler(commands='sendalladmin', state=Admin_Switch.input_off)
async def command_to_send_spam_to_users(message: Message):
    role = await db.get_permission_status(message.from_user.id)
    if role == 'admin':
        # Загрузка списка user_id и конвертация в int-список.
        try:
            file_path = Config.file_path_data_spam_id_s
            with open(file_path, 'r') as file:
                lines = file.readlines()
                users_from_file = [int(line.strip()) for line in lines]

            users_from_db = await db.get_list_users()
            buyers_from_db = await db.get_list_buyers()

            users = list(set(users_from_file + users_from_db) - set(buyers_from_db))
        except Exception as e:
            logger.exception(e)

        bot_blocked = []
        cant_initiate_conversation = []
        counter_for_spam = 0
        for user in users:
            try:
                text = '- Привет! Самое время купить билет, ведь тусовка уже завтра!' \
                       '\nЧтобы узнать подробнее, отправь мне /start'
                await bot.send_message(user, text)
                logger.info(f'Пользователь {user} получил рассылку!')
                counter_for_spam += 1
                await asyncio.sleep(0.5)
            except BotBlocked:
                bot_blocked.append(user)
                logger.info(f'Пользователь {user} заблокировал бота!')
            except CantInitiateConversation:
                cant_initiate_conversation.append(user)
            except Exception as e:
                logger.exception(e)
        logger.info(f'Количество людей, которые получили рассылку:{counter_for_spam}\n')
        logger.info(f'Список людей, которые заблокировали бота: {len(bot_blocked)} людей\n {bot_blocked}')
        logger.info(f'Список людей, с которым нельзя было начать диалог: {len(cant_initiate_conversation)} людей\n'
                    f'{cant_initiate_conversation}')


@dp.message_handler(commands='count_tickets', state="*")
async def command_to_get_count_of_buyers(message: Message):
    if message.from_user.id in Config.access_users:
        data_4_1, data_1Ticket = await db.count_by_types_tickets()
        text = (f'На текущий момент:\n'
                f'· Всего билетов: {data_4_1+data_1Ticket}\n'
                f'· Продано билетов: {data_4_1+data_1Ticket}\n'
                f'· Проходок: 0\n'
                f'\n'
                f'Билеты по категориям:\n'
                f'· Обычные билеты: {data_1Ticket}\n'
                f'· 4+1 билеты: {data_4_1}\n'
                f'· ВИП-билеты: {0}\n')

        await bot.send_message(message.from_user.id, text)


@dp.message_handler(commands='tr87a687sayaiiua', state="*")
async def command_to_get_admin_permission(message: Message):
    await db.update_role_of_user(message.from_user.id, 'admin')
    await bot.send_message(message.chat.id, 'Админ права выданы!')
    await Admin_Switch.input_off.set()
    logger.info(f'{message.chat.id} получил админ права!')
    await admin_info(message)


## Получение photo_id для телеграмма
@dp.message_handler(content_types=['photo'], state='*')
async def get_url_of_image(message: Message):
    if message.from_user.id == Config.admin_id:
        id_photo = message.photo[-1].file_id
        logger.info(id_photo)


# """"""" Розыгрыш билетов """""""
# @dp.message_handler(commands='lottery_start', state='*')
# async def start_a_lottery(message: Message):
#     if message.from_user.id == Config.admin_id:
#         photo = InputFile(Config.file_path_afisha)
#         await bot.send_photo(chat_id=Config.channel_id, photo=photo,
#                              caption=lottery_text,
#                              reply_markup=lottery_keyboard())
#
# @dp.callback_query_handler(text='lottery_join', state='*')
# async def join_to_lottery(call: CallbackQuery):
#     user = call.from_user
#     user_channel_status = await bot.get_chat_member(chat_id=Config.channel_id, user_id=user.id)
#     if user_channel_status["status"] != 'left':
#         try:
#             check = await db.exist_user(user.id)
#         except OperationalError:
#             time.sleep(0.5)
#             check = await db.exist_user(user.id)
#         if not check:
#             await db.add_users(user.id, user.first_name, user.last_name, user.username)
#         await db.join_to_lottery(user.id)
#         await call.answer('Вы участвуете в розыгрыше!', show_alert=True)
#     else:
#         await call.answer('Для участия нужно подписаться на канал!', show_alert=True)
#
# @dp.message_handler(commands='end_of_lottery', state='*')
# async def end_of_lottery(message: Message):
#     if message.from_user.id == Config.admin_id:
#         try:
#             winners = await db.stop_the_lottery()
#             i = 0
#             for user_id in winners:
#                 i += 1
#                 label = create_free_label(user_id)
#
#                 await db.add_user_to_buyers(user_id, label, 0)
#
#                 basket = [['1Ticket', 1]]
#                 await db.add_one_ticket(basket, label)
#
#                 ticket_id = await db.get_ticket_id(label, '1Ticket')
#                 name = f'Победитель розыгрыша №{i}'
#                 await db.add_ticket_name(ticket_id, name)
#
#                 img = generate_qrcode(label)
#
#                 msg = await bot.send_photo(chat_id=user_id, photo=img,
#                                            caption=message_to_winner,
#                                            reply_markup=back_to_menu())
#                 # Получение id photo на хранение
#                 photo_id = msg['photo'][-1]['file_id']
#                 await db.update_photo_id(photo_id, label)
#
#                 logger.info(f'Пользователь {user_id} победитель №{i} в розыгрыше!')
#                 await bot.send_message(chat_id=Config.admin_id, text=f'Победитель розыгрыша №{i} {user_id}')
#
#             photo = InputFile(Config.file_path_afisha)
#             await bot.send_photo(chat_id=Config.channel_id, photo=photo,
#                                  caption=lottery_final)
#         except Exception as e:
#             logger.exception(e)
#
# """"""" *************** """""""


