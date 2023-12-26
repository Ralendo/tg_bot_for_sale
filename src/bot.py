import sys
import os
# Добавляем путь ко всем файлам
sys.path.append()

from aiogram import Bot, Dispatcher
from config import Config
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import asyncio

from services.logger_settings import logger_config
import logging.config

from services import DataBase


bot = Bot(token=Config.token, parse_mode='HTML')
dp = Dispatcher(bot=bot, storage=MemoryStorage())

# Создание папки логов, если её нет
os.makedirs("src/logs", exist_ok=True)

# Инициализация логгера
logging.config.dictConfig(logger_config)
logger = logging.getLogger('tg_bot')

# Инициализация Базы Данных
db = DataBase()
logger.debug('Database is online!')


async def main() -> None:
	from handlers import dp
	try:
		logger.debug('Bot is online!')
		await bot.delete_webhook(drop_pending_updates=False)
		await dp.start_polling()
	finally:
		logger.debug('Bot is stopped!')
		await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.debug('Bot is stopped!')

