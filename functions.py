from aiogram import Bot, Dispatcher, executor, types
import re
import json
import keyboards as kb
import sqlite3

# Connect to the database
conn = sqlite3.connect("ss.db")
cursor = conn.cursor()
from datetime import datetime


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


async def validate_email(email):
    """Validate the given email address."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


async def only_numbers(text_with_nombers):
    """Extract only the numbers from a string"""
    numbers = re.findall("\d+", text_with_nombers)
    phone_number = "".join(numbers)
    return phone_number


async def register_language_if_needed(message):
    """checks if the language is in the database. If not, the user is prompted to choose a language."""
    await register_language_if_needed(message)
    language_code = await languageCoge_check(message)
    if not language_code:
        await languageLocal(message)


async def languageLocal(message=types.Message):
    """Propose to use the local language"""
    # Get the local code  and his name on local language
    languageCode = message.from_user.language_code
    localeLanguageName = message.from_user.locale.language_name
    # Create a message with buttons "yes" and "Change"
    question, markup = await kb.selectLanguageAgre(languageCode, localeLanguageName)
    await message.answer(question, reply_markup=markup)


async def implemenLanguage(call):
    """Propose to use the selected language"""
    languageCode = call.data[
        len("language=") :
    ]  # extract the value of "language" parameter
    question, markup = await kb.selectLanguageAgre(languageCode)
    await call.message.answer(question, reply_markup=markup)


async def choseLanguage(call):
    """Makes a row with possible languages by keys from file."""
    markup = await kb.languageOption()
    await call.message.answer(call.data, reply_markup=markup)


async def existanceCheck(id, now):
    """Check if the private chat is already exist, and add it if not."""
    check = cursor.execute("SELECT id FROM users WHERE id = ?;", (id,))
    if not check.fetchone():
        cursor.execute(
            "INSERT INTO users (id, registration_time_ddmmyyyyhhmm) VALUES (?, ?);",
            (id, now),
        )
        conn.commit()


async def saveLanguage(call):
    """Save the selected language"""
    id = int(call.message.chat.id)
    languageCode = call.data.split("=")[1]
    now = int(datetime.now().strftime("%d%m%Y%H%M"))
    # check if the user already in base.
    await existanceCheck(id, now)
    # Save the language.
    cursor.execute(
        "UPDATE users SET language_code = ? WHERE id = ?;", (languageCode, id)
    )
    conn.commit()
    language_is_chosen = await translate_text(languageCode, "language_is_chosen")
    await call.message.answer(
        language_is_chosen
    )  # languagePack back a List si in 1 request I add a [0].


async def languageCoge_check(message):
    """Check whether a user has already set a default language preference in the bot or not."""
    id = int(message.chat.id)

    cursor.execute("SELECT language_code FROM users WHERE id = ?;", (id,))
    result = cursor.fetchone()
    return result[0] if result else None


async def first_nameCheck(message):
    """checks if the user is registered in the database."""
    id = int(message.chat.id)
    cursor.execute("SELECT first_name FROM users WHERE id = ?;", (id,))
    result = cursor.fetchone()
    return result[0] if result else None


async def name_agree(message, language_code, first_name, last_name):
    """Agree with the names."""
    question, markup = await kb.two_InlineKeyboardButton(
        language_code, "name_agree", "yes", "change", "name agreed", "chose first_name"
    )
    question = question.format(first_name=first_name, last_name=last_name)
    await message.answer(question, reply_markup=markup)


async def first_name(call, state):
    """Input firs name"""
    first_name = call.message.chat.first_name
    data = await state.get_data()
    language_code = data.get("language_code")
    first_name_text = await translate_text(language_code, "first_name_text")
    keyboard = await kb.one_button(first_name)
    await call.message.answer(first_name_text, reply_markup=keyboard)


async def last_name(message, state):
    """Listen and save the first name and ask for input last name"""
    last_name = message.chat.last_name
    data = await state.get_data()
    language_code = data.get("language_code")
    last_name_text = await translate_text(language_code, "last_name_text")
    keyboard = await kb.one_button(last_name)
    await message.answer(last_name_text, reply_markup=keyboard)


async def ask_telephone(call, language_code):
    """Ask for telephone number"""
    send_contact, ask_for_telephone = await translate_text(
        language_code, ["send_contact", "ask_for_telephone"]
    )
    markup_request = await kb.your_phone_number(send_contact)
    await call.message.answer(ask_for_telephone, reply_markup=markup_request)


async def ask_contact(message, language_code):
    """Ask for contact"""
    reg_text, send_contact = await translate_text(
        language_code, ["reg_text", "send_contact"]
    )
    markup_request = await kb.your_phone_number(send_contact)

    await message.reply(reg_text, reply_markup=markup_request)


async def ask_email(message, state):
    """Ask for email"""
    language_code = await language_code_from_state(state)
    ask_for_email = await translate_text(language_code, "ask_for_email")
    await message.answer(ask_for_email)


async def language_code_from_state(state):
    """Extract language code"""
    data = await state.get_data()
    first_name = data.get("first_name")
    language_code = data.get("language_code")
    return language_code


async def end_registration(message, state):
    """extract all data from state and add it in to DB"""
    data = await state.get_data()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    phone_number = await only_numbers(phone_number)
    phone_number = int(phone_number)
    email = data.get("email")
    id = int(message.chat.id)
    # save into DB
    cursor.execute(
        "UPDATE users SET first_name=?, last_name=?, phone_number=?, email=? WHERE id=?;",
        (first_name, last_name, phone_number, email, id),
    )
    conn.commit()

    await send_registration_confirmation_message(message)


async def send_registration_confirmation_message(message):
    """Send a messge with thanks for registration"""
    # takes contact from DB
    id = int(message.chat.id)
    cursor.execute(
        "SELECT language_code, first_name, last_name, phone_number, email FROM users WHERE id = ?;", (id,))
    language_code, first_name, last_name, phone_number, email  = cursor.fetchone()
    conn.commit()
    # Take a text with chosen language
    thanks_for_reg = await translate_text(language_code, "reg_thanks")
    # Format text
    thanks_for_reg = thanks_for_reg.format(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,
    )
    # Send a massage
    await message.answer(thanks_for_reg)



async def is_contact_correct(message):
    '''Send a confirm message with 2 options'''
    language_code= await languageCoge_check(message)
    question, markup = await kb.two_InlineKeyboardButton(
        language_code,
        "valid_contact",
        "yes",
        "change",
        "contact correct",
        "start registration",
    )
    await message.answer(question, reply_markup=markup)



async def extract_and_save_from_contact(message, state):
    """extracts from contact data and save it"""
    phone_number = message.contact.phone_number
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    await state.update_data(phone_number=phone_number)
    await state.update_data(first_name=first_name)
    await state.update_data(last_name=last_name)
