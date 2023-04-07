from aiogram import types
import json


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
                       " If you agree, press 'Yes',\n or you can choose another language by pressing 'No'."
            languageCode = 'en'

        markup = types.InlineKeyboardMarkup()
        yes = text[languageCode]['yes']
        change = text[languageCode]['change']

        markup.row(
            types.InlineKeyboardButton(yes, callback_data=f"save the language={languageCode}"),
            types.InlineKeyboardButton(change, callback_data="chose other language"))
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