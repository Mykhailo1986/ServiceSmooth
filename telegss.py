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


@dp.message_handler(commands=["state"], state="*")
async def print_current_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await bot.send_message(chat_id=617409965, text=message.date)
    if current_state is None:
        await message.answer("The current state is not defined.")
    else:
        await message.answer(f"The current state is {current_state}")

    await fn.test(
        message,
    )


@dp.message_handler(commands=["start"], state="*")
async def start(message=types.Message, state=FSMContext):
    """It greets the user, changes the default language, and then directs them to the registration process"""
    await message.answer("HI")
    # checks if the language is in the database. If not, the user is prompted to choose a language.
    language_code = await fn.language_code_give(message, state)
    first_name = await fn.first_name_check(message)
    if not language_code:
        await language_start(message)
        return None
    # checks if the user is registered in the database. If not, the user is prompted to register.
    elif not first_name:
        await registration_start(message, state)


@dp.message_handler(commands=["help"], state="*")
async def help(message=types.Message, state=FSMContext):
    """send message about possible options"""
    language_code = await fn.language_code_give(message, state)
    if not language_code:
        await language_start(message)
        return
    await fn.help_message(message, state, language_code)


@dp.message_handler(commands=["our"], state="*")
async def our_contact(message=types.Message, state=FSMContext):
    """send message about saloon"""
    await fn.our_contact(bot, message, state)


@dp.message_handler(commands=["reg"], state="*")
async def registration_start(message=types.Message, state=FSMContext):
    """Start registration form"""
    # checks if the language is in the database. If not, the user is prompted to choose a language.
    language_code = await fn.language_code_give(message, state)
    if not language_code:
        await language_start(message)
        return
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
Looking
BEGINING
"""


@dp.message_handler(commands=["look"], state="*")
async def looking(message=types.Message, state=FSMContext):
    """Send message with your appointments"""
    language_code = await fn.language_code_give(message, state)
    if not language_code:
        await language_start(message)
        return

    (
        procedure,
        date,
        time,
        duration,
        address,
        total_priсe,
        registration_time,
        procedure_number,
        kind,
    ) = fn.nearest_appointment(message)
    if await fn.looking(
        language_code, message, procedure, date, time, duration, address, total_priсe
    ):
        await ST.ServiseSmoothState.CHOOSE_lOOK.set()


@dp.callback_query_handler(
    lambda c: c.data == "look another", state=ST.ServiseSmoothState.CHOOSE_lOOK
)
async def look_another(call, state=FSMContext):
    await fn.looking_another(call, state)


@dp.callback_query_handler(
    lambda c: c.data == "chen_del", state=ST.ServiseSmoothState.CHOOSE_lOOK
)
async def change_delete(call, state=FSMContext):
    await fn.change_delete(call, state)


@dp.callback_query_handler(
    lambda c: c.data in {"change", "cancel"}, state=ST.ServiseSmoothState.CHOOSE_lOOK
)
async def are_you_sure(call, state=FSMContext):
    await fn.are_you_sure(call, state)


@dp.callback_query_handler(
    lambda c: c.data == "change it", state=ST.ServiseSmoothState.CHOOSE_lOOK
)
async def change_date(call, state=FSMContext):
    await fn.change_date_appointment(call, state, bot)


@dp.callback_query_handler(
    lambda c: c.data == "cancel it", state=ST.ServiseSmoothState.CHOOSE_lOOK
)
async def change_date(call, state=FSMContext):
    await fn.cancel_appointment(call, state, bot)
    await state.finish()


@dp.callback_query_handler(
    lambda c: c.data == "no", state=ST.ServiseSmoothState.CHOOSE_lOOK
)
async def i_mistaken(call, state=FSMContext):
    await state.finish()


"""
Looking
END
"""


"""
Booking
BEGINING
"""


@dp.message_handler(commands=["book"], state="*")
async def booking(message=types.Message, state=FSMContext):
    # checks if the language is in the database. If not, the user is prompted to choose a language.
    language_code = await fn.language_code_give(message, state)
    if not language_code:
        await language_start(message)
        return
    else:
        await state.update_data(language_code=language_code)
    # checks if User already registered?
    first_name = await fn.first_name_check(message)
    if not first_name:
        await registration_start(message, state)
        return

    else:
        await fn.send_registration_confirmation_message(message)
    #     await ST.Booking.START_BOOK.set()
    #
    # '''ask to chose specialist'''
    #
    # # Open the  state and send in a language_code
    # language_code = await fn.language_code_give(message, state)
    #     await ST.Booking.SEL_Spec.set()
    #
    #     # propose to chose specialist
    #     await fn.ask_for_specialist(message, language_code)
    #
    # @dp.message_handler(lambda c : c.text== ("1"), state=ST.Booking.SEL_Spec )
    # async def specialist_chosen(message=types.Message, state=FSMContext):
    #     '''Message the chosen specialist'''
    #     language_code=await fn.language_code_give(message,state)
    #     await fn.specialist_name(language_code, message)
    #     # Save the specialist and kind of procedure
    #     await state.update_data(kind="massage")
    #     await state.update_data(specialist="1")
    #     # Run the message with list of procedure
    await fn.chose_massage_procedure_propose(language_code, message)
    await ST.Booking.SEL_Proc.set()

    # For 1 massagist
    await state.update_data(kind="massage")

@dp.message_handler(
    commands=['1','2','3','4','5'],
    state=ST.Booking.SEL_Proc,
)
async def procedure_chosen_by_commands(message=types.Message, state=FSMContext):
    if message.text[0] == "/":
        message.text=message.text[1]
    # take the language code
    language_code = await fn.language_code_give(message, state)
    # save the number chosen procedure
    await fn.save_chosen_procedure(message, state, language_code)
    # sand a massage the propose to choose a place
    await fn.ask_for_location(message, language_code)
    await ST.Booking.SEL_Place.set()


@dp.message_handler(
    lambda c: any(str(num) in c.text for num in range(1, 5 + 1)),
    state=ST.Booking.SEL_Proc,
)
async def procedure_chosen(message=types.Message, state=FSMContext):
    # take the language code
    language_code = await fn.language_code_give(message, state)
    # save the number chosen procedure
    await fn.save_chosen_procedure(message, state, language_code)
    # sand a massage the propose to choose a place
    await fn.ask_for_location(message, language_code)
    await ST.Booking.SEL_Place.set()


@dp.callback_query_handler(lambda c: c.data == "salon", state=ST.Booking.SEL_Place)
async def salon(call, state=FSMContext):
    """give an information about location of salon"""
    await ST.Booking.SEL_Date.set()
    # send our contact information
    await fn.our_contact(bot, call, state)
    await fn.ask_for_data(call, state)


@dp.callback_query_handler(lambda c: c.data == "my_place", state=ST.Booking.SEL_Place)
async def my_place(call, state=FSMContext):
    """Ask an information about location"""

    await ST.Booking.SEL_Place.set()
    # ask for coordinate
    await fn.ask_location(call, state)

@dp.callback_query_handler(lambda c: c.data == "back", state=ST.Booking.SEL_Place)
async def back_to_procedure(call, state=FSMContext):
    """give an information about location of salon"""
    language_code = await fn.language_code_give(call,state)
    await fn.chose_massage_procedure_propose(language_code, call)
    await ST.Booking.SEL_Proc.set()
@dp.message_handler(
    content_types=types.ContentType.LOCATION, state=ST.Booking.SEL_Place
)
async def extract_location_from_contact(message: types.Message, state=FSMContext):
    # extract the location data from the message
    longitude = message.location.longitude
    latitude = message.location.latitude
    # update the chat's state with the location data
    await state.update_data(address=[latitude, longitude])
    # send a confirmation message
    await fn.ask_for_data(message, state)
    await ST.Booking.SEL_Date.set()


@dp.message_handler(state=ST.Booking.SEL_Place)
async def take_address_from_message(message: types.Message, state=FSMContext):
    """Take and save in state address from user inputs"""
    address = message.text
    await state.update_data(
        address=address,
    )
    await fn.ask_for_data(message, state)
    await ST.Booking.SEL_Date.set()


@dp.message_handler(state=ST.Booking.SEL_Date)
async def take_day_from_user(message: types.Message, state=FSMContext):
    """Take and save in state date of appointment from user inputs, asking for time"""
    await fn.day_selector(message, state)
    if await fn.ask_for_time(message, state):
        await ST.Booking.SEL_Time.set()


@dp.message_handler(state=ST.Booking.SEL_Time)
async def take_time_from_user(message: types.Message, state=FSMContext):
    """Take and save in state time of appointment from user, send a confirmation"""
    back = await fn.back(message, state)
    if message.text == back:
        await fn.ask_for_data(message, state)
        await ST.Booking.SEL_Date.set()
    elif await fn.time_selector(message, state):
        await fn.approve_appointment(message, state)
        await ST.Booking.END_BOOK.set()
    else:
        await fn.ask_for_time(message, state)


@dp.callback_query_handler(lambda c: c.data == "book again", state=ST.Booking.END_BOOK)
async def booking_again(call, state=FSMContext):
    """return to chose the procedure"""
    language_code = await fn.language_code_give(call, state)
    message = call.message
    await fn.chose_massage_procedure_propose(language_code, message)
    await ST.Booking.SEL_Proc.set()


@dp.callback_query_handler(lambda c: c.data == "confirm", state=ST.Booking.END_BOOK)
async def confirm_appointment(call, state=FSMContext):
    await fn.confirm_appointment(call, state, bot)
    await state.finish()


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
    if message.text=="🔙":
        await ST.FirstRegistration.F_NAME_REG.set()
        await fn.first_name(message, state)
        return
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
    language_code = await fn.language_code_give(message,state)
    skip, back, valid_email = await fn.translate_text(language_code,
                                                     ["skip", "back", "valid_email"])

    if message.text == back:
        await fn.ask_telephone(message, language_code)
        await ST.FirstRegistration.TEL_REG.set()
        return
    elif message.text != skip:
        email = message.text
        # Check if the email is valid
        is_valid = await fn.validate_email(email)
        if not is_valid:
            await message.answer(valid_email)
            return
        await state.update_data(email=email)

    # Send all data from state into DB

    await fn.end_registration(message, state)
    await fn.is_contact_correct(message)
    await ST.FirstRegistration.END_REG.set()


@dp.callback_query_handler(
    lambda c: c.data == "start registration",
    state=[ST.FirstRegistration.END_REG, ST.Booking.START_BOOK],
)
async def reregistration(call, state=FSMContext):
    """Send message asking user which information they would like to correct"""
    message = call.message
    await registration_start(message, state)


@dp.callback_query_handler(
    lambda c: c.data == "contact correct", state=ST.FirstRegistration.END_REG
)
async def end_reregistration(call, state=FSMContext):
    """Send message Thanks and propose to booking an appointment"""
    await fn.end_reregistration(call, state)
    await state.finish()


"""
Registration
END
"""


"""
Language chose
BEGINING
"""


@dp.message_handler(commands=["lang"], state="*")
async def language_start(
    message=types.Message, state=ST.ServiseSmoothState.CHOOSE_LANGUAGE
):
    """Propose to use the local language"""
    await fn.propose_local_language(message)
    await ST.ServiseSmoothState.CHOOSE_LANGUAGE.set()


@dp.callback_query_handler(
    lambda c: c.data == "chose other language",
    state=ST.ServiseSmoothState.CHOOSE_LANGUAGE,
)
async def pick_language(call):
    """Make a row with possible languages by keys from file"""
    await fn.choose_language_from_available(call)


@dp.callback_query_handler(
    lambda c: c.data.startswith("language="),
    state=ST.ServiseSmoothState.CHOOSE_LANGUAGE,
)
async def implement_language(call):
    """Propose to use the selected language"""
    await fn.implement_language(call)


@dp.callback_query_handler(
    lambda c: c.data.startswith("save the language="),
    state=ST.ServiseSmoothState.CHOOSE_LANGUAGE,
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
