from aiogram import types
import json


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
# async def selectLanguageAgre(languageCode,localeLanguageName=0):
#     '''Confirm selected language'''
#     # Load the text strings from the JSON file
#     with open('text.json', 'r', encoding='utf-8') as f:
#         text = json.load(f)
#
#         # Ask a question in the user's preferred language
#         if languageCode in [keys for keys in text]:
#             question = text[languageCode]['greeting1'] + text[languageCode]['language_name'] + '\n' + \
#                        text[languageCode]['greeting2']
#
#         else:
#
#             question = "Hello, your default language is : " + localeLanguageName + ".\n" \
#                        " Unfortunately, your language is not yet supported," \
#                        " so the default language will be set to English automatically." \
#                        " If you agree, press 'Yes',\n or you can choose another language by pressing 'Chose'."
#             languageCode = 'en'
#
#         markup = types.InlineKeyboardMarkup()
#         yes = text[languageCode]['yes']
#         change = text[languageCode]['change']
#
#         markup.row(
#             types.InlineKeyboardButton(yes, callback_data=f"save the language={languageCode}"),
#             types.InlineKeyboardButton(change, callback_data="chose other language"))
#     return question, markup
async def selectLanguageAgre(languageCode,localeLanguageName=0):
    '''Confirm selected language'''


    # Load the text strings from the JSON file
    with open('text.json', 'r', encoding='utf-8') as f:
        text = json.load(f)

        # Ask a question in the user's preferred language
        if languageCode in [keys for keys in text]:
            question = text[languageCode]['greeting1'] + text[languageCode]['language_name'] + '\n' + \
                       text[languageCode]['greeting2']

        else:

            question = "Hello, your default language is : " + localeLanguageName + ".\n" \
                       " Unfortunately, your language is not yet supported," \
                       " so the default language will be set to English automatically." \
                       " If you agree, press 'Yes',\n or you can choose another language by pressing 'Chose'."
            languageCode = 'en'

    question1, markup = await two_InlineKeyboardButton(languageCode, 'greeting1', 'yes', 'change',
                                                      f"save the language={languageCode}", "chose other language")

    return question, markup
async def two_InlineKeyboardButton(languageCode,question, buttonName1, buttonName2, option1, option2):
    '''Makes 2 buttons and text'''
    question, buttonName1, buttonName2 = await translate_text(languageCode, [question,buttonName1, buttonName2])

    markup = types.InlineKeyboardMarkup()


    markup.row(
        types.InlineKeyboardButton(buttonName1, callback_data=option1),
        types.InlineKeyboardButton(buttonName2, callback_data=option2))
    return question, markup
async def languageOption():
    '''Makes a row with possible languages by keys from file.'''
    with open('text.json', 'r', encoding='utf-8') as f:
        text = json.load(f)
        markup = types.InlineKeyboardMarkup()
        markup.row(
            *[types.InlineKeyboardButton(keys, callback_data=f"language={keys}") for keys in text]
        )
    return markup

async def one_button(button_text):
    '''Create a keyboard with one button'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(button_text))
    return keyboard

async def your_phone_number(send_contact):
    '''ask for phone nomber'''
    markup_request = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True).add(
        types.KeyboardButton(send_contact, request_contact=True))
    return markup_request

# async def your_phone_number():
#     '''ask for phone nomber'''
#     markup_request = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True).add(
#         types.KeyboardButton('Отправить свой контакт ☎️', request_contact=True))
#     return markup_request