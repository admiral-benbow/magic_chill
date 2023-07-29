from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import configparser

# getting a bot_token from our .ini file

config = configparser.ConfigParser()    # parser-object
config.read("config.ini")
BOT_TOKEN = config["BOT"]["token"]
print(BOT_TOKEN)

# Creating a memory storage to use in the bot (in the dispatcher), in RAM
storage = MemoryStorage()

# creating a bot-оbject and its dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=storage)
