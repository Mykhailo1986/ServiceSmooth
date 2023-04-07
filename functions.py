from aiogram import Bot, Dispatcher, executor, types

import json
import keyboards as kb
import sqlite3
# Connect to the database
conn = sqlite3.connect('ss.db')
cursor = conn.cursor()
from datetime import datetime


async def translate_text(languageCode, request):
    '''Search the text in correct language.'''
    # Load the text strings from the JSON file
    with open('text.json', 'r', encoding='utf-8') as f:
        text = json.load(f)

    # Check if request is a string or a list
    if isinstance(request, str):
        response = text[languageCode][request]
    else:
        # Loop through each string in the request and get the corresponding translation
        response = []
        for string in request:
            translation = text.get(languageCode, {}).get(string, None)
            response.append(translation)

    return response

async def languageLocal(message=types.Message):
    '''Propose to use the local language'''
    #Get the local code  and his name on local language
    languageCode = message.from_user.language_code
    localeLanguageName = message.from_user.locale.language_name

    question, markup = await kb.selectLanguageAgre(languageCode,localeLanguageName)
    await  message.reply(question, reply_markup=markup)

async def implemenLanguage(call):
    '''Propose to use the selected language'''
    languageCode = call.data[len("language="):]  # extract the value of "language" parameter
    question, markup = await kb.selectLanguageAgre(languageCode)
    await  call.message.reply(question, reply_markup=markup)

async def choseLanguage(call):
    '''Makes a row with possible languages by keys from file.'''
    markup= await kb.languageOption()
    await call.message.answer(call.data, reply_markup=markup)

async def existanceCheck(id, now):
    '''Check if the private chat is already exist, and add it if not.'''
    check = cursor.execute("SELECT id FROM users WHERE id = ?;", (id,))
    if not check.fetchone():
        cursor.execute("INSERT INTO users (id, registration_time_ddmmyyyyhhmm) VALUES (?, ?);", (id, now))
        conn.commit()

async def saveLanguage(call):
    '''Save the selected language'''
    id = int(call.message.chat.id)
    languageCode = call.data.split("=")[1]
    now = int(datetime.now().strftime("%d%m%Y%H%M"))
    # check if the user already in base.
    await existanceCheck(id, now)
    # Save the language.
    cursor.execute("UPDATE users SET language_code = ? WHERE id = ?;", (languageCode, id))
    conn.commit()
    language_is_chosen = await translate_text(languageCode, "language_is_chosen")
    await call.message.answer(language_is_chosen)#languagePack back a List si in 1 request I add a [0].

async def languageCoge_check(message):

    id =  int(message.chat.id)
    cursor.execute("SELECT language_code FROM users WHERE id = ?;", (id,))
    result = cursor.fetchone()
    return result[0] if result else None

async def first_nameCheck(message):
    id =  int(message.chat.id)
    cursor.execute("SELECT first_name FROM users WHERE id = ?;", (id,))
    result = cursor.fetchone()
    return result[0] if result else None


async def name_agree(message,language_code,first_name,last_name):
    '''Agree with the names.'''
    question, markup = await kb.two_InlineKeyboardButton(language_code, 'name_agree', 'yes', 'change',
                                                       "name agreed", "chose first_name")
    question = question.format(first_name=first_name,last_name=last_name)
    await  message.reply(question, reply_markup=markup)

async def first_name(call,state):
    '''Input firs name'''
    first_name = call.message.chat.first_name
    data = await state.get_data()
    language_code = data.get('language_code')
    first_name_text= await translate_text(language_code,'first_name_text')
    keyboard= await kb.one_button(first_name)
    await call.message.reply(first_name_text, reply_markup=keyboard)

async def last_name(message,state):
    '''Listen and save First name and Input last name'''
    last_name = message.chat.last_name
    data = await state.get_data()
    language_code = data.get('language_code')
    last_name_text= await translate_text(language_code,'last_name_text')
    keyboard= await kb.one_button(last_name)
    await message.reply(last_name_text, reply_markup=keyboard)







