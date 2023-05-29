import config
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
