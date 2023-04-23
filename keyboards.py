from aiogram import types
import json


async def translate_text(language_code, request):
    """Search the text in correct language."""
    # Load the text strings from the JSON file
    with open("text.json", "r", encoding="utf-8") as f:
        text = json.load(f)

    # Check if request is a string or a list
    if isinstance(request, str):
        response = text[language_code][request]
    else:
        # Loop through each string in the request and get the corresponding translation
        response = []
        for string in request:
            translation = text.get(language_code, {}).get(string, None)
            response.append(translation)

    return response


async def selectLanguageAgre(language_code, localeLanguageName=None):
    """Confirm selected language"""

    # Load the text strings from the JSON file
    with open("text.json", "r", encoding="utf-8") as f:
        text = json.load(f)

        # Ask a question in the user's preferred language
        if language_code in [keys for keys in text]:
            question = (
                text[language_code]["greeting1"]
                + text[language_code]["language_name"]
                + "\n"
                + text[language_code]["greeting2"]
            )

        else:

            question = (
                "Hello, your default language is : " + localeLanguageName + ".\n"
                " Unfortunately, your language is not yet supported,"
                " so the default language will be set to English automatically."
                " If you agree, press 'Yes',\n or you can choose another language by pressing 'Chose'."
            )
            language_code = "en"

    question1, markup = await two_InlineKeyboardButton(
        language_code,
        "greeting1",
        "yes",
        "change",
        f"save the language={language_code}",
        "chose other language",
    )

    return question, markup

async def one_InlineKeyboardButton(
     buttonName1, option1
):
    """Return markup for a single button without translation text
    takes the button text in this form ("buttonName", "option")
    """


    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(buttonName1, callback_data=option1),

    )
    return  markup
async def two_InlineKeyboardButton(
    languageCode, question, buttonName1, buttonName2, option1, option2
):
    """Makes 2 buttons and translated text"""
    question, buttonName1, buttonName2 = await translate_text(
        languageCode, [question, buttonName1, buttonName2]
    )

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(buttonName1, callback_data=option1),
        types.InlineKeyboardButton(buttonName2, callback_data=option2),
    )
    return question, markup


async def InlineKeyboardButton_plural(request):
    """Return markups without translation text
    takes the request in this form (("buttonName1", "option1"),("buttonName2",  option2"))
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(
        *[
            types.InlineKeyboardButton(button_text[0], callback_data=button_text[1])
            for button_text in request
        ]
    )
    return markup


async def languageOption():
    """Makes a row with possible languages by keys from file."""
    with open("text.json", "r", encoding="utf-8") as f:
        text = json.load(f)
        markup = types.InlineKeyboardMarkup()
        markup.row(
            *[
                types.InlineKeyboardButton(keys, callback_data=f"language={keys}")
                for keys in text
            ]
        )
    return markup


async def one_button(button_text):
    """Create a keyboard with one button"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(button_text))
    return keyboard


async def plural_buttons(request, in_row=3):

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True, row_width=in_row
    )
    keyboard.add(*[types.KeyboardButton(button_text) for button_text in request])

    return keyboard


async def your_phone_number(send_contact):
    """ask for phone number"""
    markup_request = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(types.KeyboardButton(send_contact, request_contact=True))
    return markup_request


async def your_location(send_location):
    """ask for your location"""
    markup_request = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(types.KeyboardButton(send_location, request_location=True))
    return markup_request
