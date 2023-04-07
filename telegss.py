from aiogram import Bot, Dispatcher, executor, types
from states import ServiseSmoothState as ST
from dotenv import load_dotenv
import os
import logging

# import json
import functions as fn
logging.basicConfig(level=logging.INFO)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware


load_dotenv()




bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['lang'],state='*')
async def languageLocal(message=types.Message,state=ST.CHOOSE_LANGUAGE):
    '''Propose to use the local language'''
    await fn.languageLocal(message)
    await ST.CHOOSE_LANGUAGE.set()
    #await  bot.delete_message(message.chat.id, message.message_id -1)

@dp.callback_query_handler(lambda c: c.data == "chose other language",state=ST.CHOOSE_LANGUAGE)
async def choseLanguage(call):
    '''Make a row with possible languages by keys from file'''
    await fn.choseLanguage(call)

@dp.callback_query_handler(lambda c: c.data.startswith("language="),state=ST.CHOOSE_LANGUAGE)
async def implemenLanguage(call):
    '''Propose to use the selected language'''
    await fn.implemenLanguage(call)

@dp.callback_query_handler(lambda c: c.data.startswith("save the language="),state=ST.CHOOSE_LANGUAGE)
async def saveLanguage(call,state=ST.CHOOSE_LANGUAGE):
    '''Save the selected language'''
    await fn.saveLanguage(call)
    await state.finish()




executor.start_polling(dp)
