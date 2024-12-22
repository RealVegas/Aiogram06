from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config_data.bot_config import BOT_TOKEN

# Инициализация логирования
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='100 MB', compression='zip')

# Инициализация бота
bot: Bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
state_storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(storage=state_storage)