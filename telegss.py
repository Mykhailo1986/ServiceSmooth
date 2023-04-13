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
    language_code=await fn.language_code_give(message,state)
    if not language_code:
        await language_start(message)

    # TODO: Make run code below is only executed after the previous code has finished running
    # checks if the user is registered in the database. If not, the user is prompted to register.
    # first_name = await fn.first_nameCheck(message)
    # if not first_name:
    #      await registration_start(message,state)
# @dp.message_handler(commands=["exit"], state="*")
# async def exit(message=types.Message, state=FSMContext):
#     await fn.exit(message.state)
#     await start(message,state)
@dp.message_handler(commands=["reg"], state="*")
async def registration_start(message=types.Message, state=FSMContext):
    """Start registration form"""
    # checks if the language is in the database. If not, the user is prompted to choose a language.
    language_code=await fn.language_code_give(message,state)
    if not language_code:
        await language_start(message)
    # Propose to send a contact from user
    await fn.ask_contact(message, language_code)
    # Create a form for input the names or implement it automatically
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    await fn.name_agree(message, language_code, first_name, last_name)
    # add the language_code in state
    await ST.FirstRegistration.F_NAME_REG.set()
    await state.update_data(language_code=language_code)

"""
Booking
BEGINING
"""
@dp.message_handler(commands=["book"], state="*")
async def booking(message=types.Message, state=FSMContext):
    # checks if the language is in the database. If not, the user is prompted to choose a language.
    language_code=await fn.language_code_give(message,state)
    if not language_code:
        await language_start(message)
    # checks if User already registered?
    first_name = await fn.first_name_check(message)
    if not first_name:
         await registration_start(message,state)
    else:
        await fn.registration_booking(message,language_code)
    # Open the booking state and send in a language_code
    await ST.Booking.START_BOOK.set()
    await state.update_data(language_code=language_code)
#     # propose to chose specialist
#     await fn.ask_for_specialist(message, language_code)
#
# @dp.message_handler(lambda c : c.text== ("1"), state=ST.Booking.START_BOOK )
# async def spcialist_cosen(message=types.Message, state=FSMContext):
#     '''Mesage the shoisen specialist'''
#     language_code=await fn.language_code_give(message,state)
#     await fn.specialist_name(language_code, message)
#     # Save the specialist and kind of procedure
#     await state.update_data(kind="massage")
#     await state.update_data(specialict="1")
#     # Run the messege with list of procedure
    await fn.chose_massage_procedure_propose(language_code, message)
    await ST.Booking.SEL_Rroc.set()


@dp.message_handler(lambda c: any(str(num) in c.text for num in range(1, 5+1)),state=ST.Booking.SEL_Rroc )
async def procedure_chosen(message=types.Message, state=FSMContext):
    # take the language code
    language_code = await fn.language_code_give(message, state)
    # save the number chosen procedure
    await fn.save_chosen_procedure(message, state, language_code)
    # sand a massage the propose to choose a place
    await fn.ask_for_location(message,language_code)

@dp.message_handler(state=ST.Booking.SEL_Rroc )
async def procedure_chosen2(message=types.Message, state=FSMContext):
    language_code = await fn.language_code_give(message, state)
    await fn.chose_massage_procedure_propose(language_code, message)

@dp.callback_query_handler(lambda c: c.data == "salon",state=ST.Booking.SEL_Rroc)
async def salon(call, state=FSMContext):
    '''give an information about location of salon'''
    await call.message.answer("У HАС")
    await state.update_data(place=call.data)
    await ST.Booking.SEL_Place.set()
  
    await bot.send_location(call.message.chat.id, latitude= 50.452951, longitude= 30.523853,proximity_alert_radius=60)




@dp.callback_query_handler(lambda c: c.data == "my_place",state=ST.Booking.SEL_Rroc)
async def salon(call, state=FSMContext):
    '''give an information about location of salon'''
    await state.update_data(place=call.data)
    await call.message.answer("У BАС")
    await ST.Booking.SEL_Place.set()




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
async def language_start(message=types.Message, state=ST.ServiseSmoothState.CHOOSE_LANGUAGE):
    """Propose to use the local language"""
    await fn.propose_local_language(message)
    await ST.ServiseSmoothState.CHOOSE_LANGUAGE.set()


@dp.callback_query_handler(
    lambda c: c.data == "chose other language", state=ST.ServiseSmoothState.CHOOSE_LANGUAGE
)
async def pick_language(call):
    """Make a row with possible languages by keys from file"""
    await fn.choose_language_from_available(call)


@dp.callback_query_handler(
    lambda c: c.data.startswith("language="), state=ST.ServiseSmoothState.CHOOSE_LANGUAGE
)
async def implement_language(call):
    """Propose to use the selected language"""
    await fn.implement_language(call)


@dp.callback_query_handler(
    lambda c: c.data.startswith("save the language="), state=ST.ServiseSmoothState.CHOOSE_LANGUAGE
)
async def saveLanguage(call, state=ST.ServiseSmoothState.CHOOSE_LANGUAGE):
    """Save the selected language"""
    await fn.save_language_in_DB(call)
    await state.finish()

"""
Language chose
END
"""

executor.start_polling(dp)
