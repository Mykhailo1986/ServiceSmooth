from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv
import logging
import os

import functions as fn
import states as ST

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())




@dp.message_handler(commands=["start"], state="*")
async def start(message=types.Message, state=FSMContext):
    """It greets the user, changes the default language, and then directs them to the registration process"""
    await message.answer("HI")
    # checks if the language is in the database. If not, the user is prompted to choose a language.
    id = int(message.chat.id)
    language_code = await fn.languageCoge_check(id)
    if not language_code:
        await languageLocal(message)

    # TODO: Make run code below is only executed after the previous code has finished running
    # checks if the user is registered in the database. If not, the user is prompted to register.
    # first_name = await fn.first_nameCheck(message)
    # if not first_name:
    #      await registration_start(message,state)


@dp.message_handler(commands=["reg"], state="*")
async def registration_start(message=types.Message, state=FSMContext):
    """Start registration form"""
    # checks if the language is in the database. If not, the user is prompted to choose a language.
    id = int(message.chat.id)
    language_code = await fn.languageCoge_check(id)
    if not language_code:
        await languageLocal(message)
    # Propose to send a contact from user
    await fn.ask_contact(message, language_code)
    # Create a form for input the names or implement it automatically
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    await fn.name_agree(message, language_code, first_name, last_name)
    # add the language_code in state
    await ST.FirstRegistration.F_NAME_REG.set()
    await state.update_data(language_code=language_code)


@dp.message_handler(commands=["book"], state="*")
async def booking(message=types.Message, state=FSMContext):
    # checks if the language is in the database. If not, the user is prompted to choose a language.
    id = int(message.chat.id)
    language_code = await fn.languageCoge_check(id)
    if not language_code:
        await languageLocal(message)
    # checks if User allredy registrated?
    first_name = await fn.first_nameCheck(message)
    if not first_name:
         await registration_start(message,state)
    else:
        await fn.registration_booking(message,language_code)
    await ST.Booking.START_BOOK.set()
    await state.update_data(language_code=language_code)
    await spsialist1(message,state)


@dp.message_handler(commands=["1"], state=ST.Booking.START_BOOK)
async def spsialist1(message=types.Message, state=FSMContext):
    id = int(message.chat.id)
    language_code = await fn.languageCoge_check(id)
    if not language_code:
        await languageLocal(message)
    await fn.specialist_name(language_code, message)
    # await fn.chose_procedure_propose(language_code, message)
@dp.message_handler(commands=["propos"], state="*")
async def Proposition(message=types.Message, state=FSMContext):
    id = int(message.chat.id)
    language_code = await fn.languageCoge_check(id)
    if not language_code:
        await languageLocal(message)

    await fn.chose_procedure_propose(language_code, message)

"""
Booking
BEGINING
"""

@dp.message_handler(commands=["1"], state="ST.Booking.START_BOOK")
async def firt_option(message=types.Message, state=FSMContext):
    await message.answer("виберете процедуру:")


"""
Boking
END
"""

"""
Regestration
BEGINING
"""
@dp.message_handler(
    content_types=types.ContentType.CONTACT, state=ST.FirstRegistration.F_NAME_REG
)
async def extract_from_contact(message: types.Message, state=FSMContext):
    """extracts from contact data and save it"""
    await fn.extract_and_save_from_contact(message, state)
    # send the message to aks an Email
    await fn.ask_email(message, state)
    await ST.FirstRegistration.EMAIL_REG.set()


@dp.callback_query_handler(
    lambda c: c.data == "chose first_name", state=ST.FirstRegistration.F_NAME_REG
)
async def input_first_name(call, state=FSMContext):
    """Ask for firs name"""
    await fn.first_name(call, state)


@dp.message_handler(state=ST.FirstRegistration.F_NAME_REG)
async def input_last_name(message=types.Message, state=FSMContext):
    """Send first name into the state, Ask for last name"""
    # Hear the first name
    first_name = message.text
    # Send first name into the state
    await state.update_data(first_name=first_name)
    # Ask for last name
    await fn.last_name(message, state)
    await ST.FirstRegistration.L_NAME_REG.set()


@dp.message_handler(state=ST.FirstRegistration.L_NAME_REG)
async def listen_last_name(message=types.Message, state=FSMContext):
    """Listen the last name"""
    # Hear the last name
    last_name = message.text
    # Send last name into the state
    await state.update_data(last_name=last_name)
    # Call for names from state
    data = await state.get_data()
    first_name = data.get("first_name")
    language_code = data.get("language_code")
    # Confirm the name or go to input it again
    await fn.name_agree(message, language_code, first_name, last_name)
    await ST.FirstRegistration.F_NAME_REG.set()


@dp.callback_query_handler(
    lambda c: c.data == "name agreed", state=ST.FirstRegistration.F_NAME_REG
)
async def apply_names(call, state=FSMContext):
    """Input a first and lust names automatically if it not exist"""
    # Call for names from state
    data = await state.get_data()
    first_name = data.get("first_name")
    language_code = data.get("language_code")
    # if not in state take from chat
    if not first_name:
        first_name = call.message.chat.first_name
        last_name = call.message.chat.last_name
        await state.update_data(first_name=first_name)
        await state.update_data(last_name=last_name)
    # Ask for telephone
    await fn.ask_telephone(call, language_code)
    await ST.FirstRegistration.TEL_REG.set()


@dp.message_handler(
    content_types=types.ContentType.CONTACT, state=ST.FirstRegistration.TEL_REG
)
async def extract_phone_number_from_contact(message: types.Message, state=FSMContext):
    """extracts the phone number from a contact"""
    # Hear a phone number
    phone_number = message.contact.phone_number
    # Save a  phone number
    await state.update_data(phone_number=phone_number)
    # Ask for an E-Mail
    await fn.ask_email(message, state)
    await ST.FirstRegistration.EMAIL_REG.set()


@dp.message_handler(state=ST.FirstRegistration.TEL_REG)
async def handler_phone_number(message=types.Message, state=FSMContext):
    """Listen the phone number and save it"""
    phone_number = message.text
    await state.update_data(phone_number=phone_number)
    # Ask for an E-Mail
    await fn.ask_email(message, state)
    await ST.FirstRegistration.EMAIL_REG.set()


@dp.message_handler(state=ST.FirstRegistration.EMAIL_REG)
async def handler_email(message=types.Message, state=FSMContext):
    """Listen the E-Mail and save all"""
    email = message.text
    # Check if the email is valid
    is_valid = await fn.validate_email(email)
    if not is_valid:
        await message.answer("Please enter a valid email address.")
        return
    await state.update_data(email=email)

    # Send all data from state into DB

    await fn.end_registration(message, state)
    await fn.is_contact_correct(message)
@dp.callback_query_handler(lambda c: c.data == "contact correct", state=ST.FirstRegistration.EMAIL_REG)
async def registration_correct(call,state=FSMContext ):
    """Send message with thanks for registration"""
    await fn.thanks(call)
    # Close the state
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "start registration", state=ST.FirstRegistration.EMAIL_REG)
async def reregistration(call,state=FSMContext ):
    """Send message asking user which information they would like to correct """
    message=call.message
    await registration_start(message, state)
"""
Registration
END
"""


"""
Language chose
BEGINING
"""
@dp.message_handler(commands=["lang"], state="*")
async def languageLocal(message=types.Message, state=ST.ServiseSmoothState.CHOOSE_LANGUAGE):
    """Propose to use the local language"""
    await fn.languageLocal(message)
    await ST.ServiseSmoothState.CHOOSE_LANGUAGE.set()


@dp.callback_query_handler(
    lambda c: c.data == "chose other language", state=ST.ServiseSmoothState.CHOOSE_LANGUAGE
)
async def choseLanguage(call):
    """Make a row with possible languages by keys from file"""
    await fn.choseLanguage(call)


@dp.callback_query_handler(
    lambda c: c.data.startswith("language="), state=ST.ServiseSmoothState.CHOOSE_LANGUAGE
)
async def implemenLanguage(call):
    """Propose to use the selected language"""
    await fn.implemenLanguage(call)


@dp.callback_query_handler(
    lambda c: c.data.startswith("save the language="), state=ST.ServiseSmoothState.CHOOSE_LANGUAGE
)
async def saveLanguage(call, state=ST.ServiseSmoothState.CHOOSE_LANGUAGE):
    """Save the selected language"""
    await fn.saveLanguage(call)
    await state.finish()

"""
Language chose
END
"""

executor.start_polling(dp)
