from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from states import ServiseSmoothState as SSS
import states as ST
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


@dp.message_handler(commands=['start'],state='*')
async def start(message=types.Message):
    '''Say hello to the user, than change the defatul language, and go to the registration '''
    await message.answer("HI")
    language_code = await fn.languageCoge_check(message)
    if not language_code:
         await languageLocal(message)
    first_name = await fn.first_nameCheck(message)
    if not first_name:
         await registration_start(message)


@dp.message_handler(commands=['reg'], state='*')
async def registration_start(message=types.Message, state=FSMContext):
    language_code = await fn.languageCoge_check(message)
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    await fn.name_agree(message,language_code,first_name,last_name)
    await state.update_data(language_code=language_code)
    await ST.FirstRegistration.F_NAME_REG.set()



@dp.callback_query_handler(lambda c: c.data == "chose first_name", state = ST.FirstRegistration.F_NAME_REG)
async def input_first_name(call,state=FSMContext):
    '''Input firs name'''
    await fn.first_name(call, state)


@dp.message_handler(state = ST.FirstRegistration.F_NAME_REG)
async def input_last_name(message=types.Message,state=FSMContext):
    '''Input last name'''
    first_name = message.text
    await state.update_data(first_name=first_name)
    await fn.last_name(message, state)
    await ST.FirstRegistration.L_NAME_REG.set()

@dp.message_handler(state = ST.FirstRegistration.L_NAME_REG)
async def listen_last_name(message=types.Message,state=FSMContext):
    '''listen last name'''
    last_name = message.text
    await state.update_data(last_name=last_name)
    data = await state.get_data()
    first_name = data.get('first_name')
    language_code = data.get('language_code')
    await fn.name_agree(message, language_code, first_name, last_name)
    await ST.FirstRegistration.F_NAME_REG.set()

@dp.callback_query_handler(lambda c: c.data == "name agreed", state = ST.FirstRegistration.F_NAME_REG)
async def apply_names(call,state=FSMContext):
    '''input a first and lust names automatically if it not exist'''
    data = await state.get_data()
    first_name = data.get('first_name')
    if not first_name:
        first_name = call.message.chat.first_name
        last_name = call.message.chat.last_name
        await state.update_data(first_name=first_name)
        await state.update_data(last_name=last_name)
    await ST.FirstRegistration.TEL_REG.set()

@dp.message_handler(state = ST.FirstRegistration.TEL_REG)
async def listen_last_name(message=types.Message,state=FSMContext):
    data = await state.get_data()
    first_name = data.get('first_name')
    await message.answer(f"hello{first_name}")










#
#
# @dp.message_handler(state=ST.FirstRegistration.START_REG)
# async def tower(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     language_code = data.get('language_code')
#     first_name = await fn.first_nameCheck(message)
#     enter_first_name = 1


@dp.message_handler(commands=['lang'],state='*')
async def languageLocal(message=types.Message, state=SSS.CHOOSE_LANGUAGE):
    '''Propose to use the local language'''
    await fn.languageLocal(message)
    await SSS.CHOOSE_LANGUAGE.set()



@dp.callback_query_handler(lambda c: c.data == "chose other language", state=SSS.CHOOSE_LANGUAGE)
async def choseLanguage(call):
    '''Make a row with possible languages by keys from file'''
    await fn.choseLanguage(call)

@dp.callback_query_handler(lambda c: c.data.startswith("language="), state=SSS.CHOOSE_LANGUAGE)
async def implemenLanguage(call):
    '''Propose to use the selected language'''
    await fn.implemenLanguage(call)

@dp.callback_query_handler(lambda c: c.data.startswith("save the language="), state=SSS.CHOOSE_LANGUAGE)
async def saveLanguage(call, state=SSS.CHOOSE_LANGUAGE):
    '''Save the selected language'''
    await fn.saveLanguage(call)
    await state.finish()




executor.start_polling(dp)


