from aiogram import types
import re
from dotenv import load_dotenv

import os
import json
import keyboards as kb
import sqlite3
import datetime
import states as ST
from calendar_client import calendar, calendar_id, create_event_body


load_dotenv()
# Connect to the database
conn = sqlite3.connect(os.getenv("DB"))
cursor = conn.cursor()
# from datetime import datetime

# working_time = {"work_start": datetime.time(8, 0), "work_end": datetime.time(22, 0)}
rest_days = [datetime.date(2023, 4, 16), datetime.date(2023, 4, 17)]

specialist = os.getenv("ADMIN")
"""FOR MAX procedure search for n=5
    look in procedure_chosen in telegrass.py
    and look in text.json FROM line "act_1_1" ... TO line "time_act_1_5"
"""
"""status:
None = not ended 
 1 = correct agried with user
 2 = not fit in time
 3 = changed by user
 0 = cancelled by user
 """


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


def only_numbers(text_with_numbers):
    """Extract only the numbers from a string"""
    numbers = re.findall("\d+", text_with_numbers)
    phone_number = "".join(numbers)
    return phone_number


def obj_processor(obj):
    """return message from call and message type"""
    if isinstance(obj, types.Message):
        message = obj
    elif isinstance(obj, types.CallbackQuery):
        message = obj.message
    return message


async def language_coge_from_DB(id):
    """Check whether a user has already set a default language preference in the bot or not."""
    cursor.execute("SELECT language_code FROM users WHERE id = ?;", (id,))
    result = cursor.fetchone()
    return result[0] if result else None


async def language_code_from_state(state):
    """Extract language code"""
    data = await state.get_data()
    language_code = data.get("language_code")

    return language_code


async def language_code_give(obj, state):
    """Give back the language_code"""
    language_code = await language_code_from_state(state)
    if not language_code:
        message = obj_processor(obj)
        id = int(message.chat.id)
        language_code = await language_coge_from_DB(id)
        if not language_code:
            keyboards = await kb.one_button("/lang")
            await message.answer(
                "ONG!!! You didn't chose the language. Tap on /lang",
                reply_markup=keyboards,
            )
    return language_code


async def register_language_if_needed(message):
    """checks if the language is in the database. If not, the user is prompted to choose a language."""
    id = int(message.chat.id)
    language_code = await language_coge_from_DB(id)
    if not language_code:
        await propose_local_language(message)


async def propose_local_language(message=types.Message):
    """Propose to use the local language"""
    # Get the local code  and his name on local language
    languageCode = message.from_user.language_code
    localeLanguageName = message.from_user.locale.language_name
    # Create a message with buttons "yes" and "Change"
    question, markup = await kb.selectLanguageAgre(languageCode, localeLanguageName)
    await message.answer(question, reply_markup=markup)


async def implement_language(call):
    """Propose to use the selected language"""
    languageCode = call.data[
        len("language=") :
    ]  # extract the value of "language" parameter
    question, markup = await kb.selectLanguageAgre(languageCode)
    await call.message.answer(question, reply_markup=markup)


async def choose_language_from_available(call):
    """Makes a row with possible languages by keys from file."""
    markup = await kb.languageOption()
    await call.message.answer(call.data, reply_markup=markup)


async def existanceCheck(id, now):
    """Check if the private chat is already exist, and add it if not."""
    check = cursor.execute("SELECT id FROM users WHERE id = ?;", (id,))
    if not check.fetchone():
        cursor.execute(
            "INSERT INTO users (id, registration_time) VALUES (?, ?);",
            (id, now),
        )
        conn.commit()


async def save_language_in_DB(call):
    """Save the selected language"""
    id = int(call.message.chat.id)
    languageCode = call.data.split("=")[1]
    now = call.message.date
    # check if the user already in base.
    await existanceCheck(id, now)
    # Save the language.
    cursor.execute(
        "UPDATE users SET language_code = ? WHERE id = ?;", (languageCode, id)
    )
    conn.commit()
    language_is_chosen = await translate_text(languageCode, "language_is_chosen")
    key = await kb.one_button("/reg")
    await call.message.answer(
        language_is_chosen, reply_markup=key
    )  # languagePack back a List si in 1 request I add a [0].


async def first_name_check(message):
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


async def first_name(obj, state):
    """Input firs name"""
    message = obj_processor(obj)
    first_name = message.chat.first_name
    data = await state.get_data()
    language_code = data.get("language_code")
    first_name_text = await translate_text(language_code, "first_name_text")
    keyboard = await kb.one_button(first_name)
    await message.answer(first_name_text, reply_markup=keyboard)


async def last_name(message, state):
    """Listen and save the first name and ask for input last name"""
    last_name = message.chat.last_name
    data = await state.get_data()
    language_code = data.get("language_code")
    last_name_text, your_first_name, back = await translate_text(
        language_code, ["last_name_text", "your_first_name", "back"]
    )
    keyboard = await kb.one_button(last_name)
    keyboard = await kb.plural_buttons([last_name, back])
    await message.answer(f"{your_first_name}{message.text}")

    await message.answer(last_name_text, reply_markup=keyboard)


async def back(obj, state):
    language_code = await language_code_give(obj, state)
    back = await translate_text(language_code, "back")
    return back


async def ask_telephone(obj, language_code):
    """Ask for telephone number"""
    message = obj_processor(obj)
    send_contact, ask_for_telephone = await translate_text(
        language_code, ["send_contact", "ask_for_telephone"]
    )
    markup_request = await kb.your_phone_number(send_contact)
    await message.answer(ask_for_telephone, reply_markup=markup_request)


async def ask_contact(message, language_code):
    """Ask for contact"""
    reg_text, send_contact = await translate_text(
        language_code, ["reg_text", "send_contact"]
    )
    markup_request = await kb.your_phone_number(send_contact)

    await message.answer(reg_text, reply_markup=markup_request)


async def ask_email(message, state):
    """Ask for email"""
    language_code = await language_code_give(message, state)
    ask_for_email = await translate_text(language_code, "ask_for_email")
    ask_for_email, skip, back = await translate_text(
        language_code, ["ask_for_email", "skip", "back"]
    )

    keyboard = await kb.plural_buttons([skip, back])
    await message.answer(ask_for_email, reply_markup=keyboard)


async def end_registration(message, state):
    """extract all data from state and add it in to DB"""
    data = await state.get_data()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    # Prepare the telephone number to save in DB
    phone_number = only_numbers(phone_number)
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
    """Send a message with thanks for registration"""
    # takes contact from DB
    id = int(message.chat.id)
    cursor.execute(
        "SELECT language_code, first_name, last_name, phone_number, email FROM users WHERE id = ?;",
        (id,),
    )
    language_code, first_name, last_name, phone_number, email = cursor.fetchone()
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
    """Send a confirm message with 2 options"""
    id = int(message.chat.id)
    language_code = await language_coge_from_DB(id)
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


async def end_reregistration(call, state):
    """send message with info that registration is end,  and propose to choise booking the appointment or look onother options"""
    language_code = await language_code_give(call, state)
    end_reg = await translate_text(language_code, "end_reg")
    key = await kb.plural_buttons(("/book", "/help"))
    await call.message.answer(end_reg, reply_markup=key)


async def ask_for_specialist(message, language_code):
    """Propose to choose the specialist"""
    ask_specialist = await translate_text(language_code, "ask_specialist")
    keyboards = await kb.one_button("1")
    await message.answer(ask_specialist, reply_markup=keyboards)


async def specialist_name(language_code, message):
    """Send the name of specialist"""
    specialist_name = await translate_text(language_code, "specialist_name1")
    await message.answer(specialist_name)


async def chose_massage_procedure_propose(language_code, obj):
    """Send a message with the available procedure options."""
    message = obj_processor(obj)
    chose_procedure = await translate_text(language_code, "chose_procedure")
    await message.answer(chose_procedure)
    # n is maximum number of procedure to chose
    n = 5
    propose = ""
    keys = []
    # Load the text strings from the JSON file
    with open("text.json", "r", encoding="utf-8") as f:
        text = json.load(f)
        n += 1
        for i in range(1, n):
            propose += (
                f"/{i} "
                + text[language_code][f"act_1_{i}"]
                + "\t"
                + text[language_code][f"time_act_1_{i}"]
                + text[language_code][f"min"]
                + "\t"
                + text[language_code][f"price_act_1_{i}"]
                + text[language_code][f"currency"]
                + "\n\n"
            )
            keys.append(
                f"{i} " + text[language_code][f"act_1_{i}"],
            )
    keyboard = await kb.plural_buttons(keys, in_row=1)
    await message.answer(propose, reply_markup=keyboard)


async def save_chosen_procedure(message, state, language_code):
    """Saves the chosen procedure and it duration into the state"""
    # take a number of procedure
    procedure_number = message.text[0]
    # save it into state
    await state.update_data(procedure_number=procedure_number)
    # takes phrases in default language

    you_chose, description, duration, act = await translate_text(
        language_code,
        (
            "you_chose",
            f"act_1_{procedure_number}_descr",
            f"time_act_1_{procedure_number}",
            f"act_1_{procedure_number}",
        ),
    )

    duration = only_numbers(duration)
    await state.update_data(duration=int(duration))
    # send message with chosen procedure
    await message.answer(
        f"{you_chose}: {act}", reply_markup=types.ReplyKeyboardRemove()
    )

    # send message with description of procedure
    await message.answer(description)


async def ask_for_location(message, language_code):
    """Propose to chose a place"""
    place, my_place, salon, back = await translate_text(
        language_code, ("place", "my_place", "salon", "back")
    )
    keyboard = await kb.InlineKeyboardButton_plural(
        ((salon, "salon"), (my_place, "my_place"), (back, "back"))
    )
    await message.answer(place, reply_markup=keyboard)


async def our_contact(bot, obj, state):
    """give an information about location of salon and save choise in state"""
    language_code = await language_code_give(obj, state)
    message = obj_processor(obj)
    # send a message to user
    salon_location = await translate_text(language_code, "salon_location")
    # send a place into state
    await state.update_data(address="salon")
    await message.answer(salon_location, reply_markup=types.ReplyKeyboardRemove())
    # # send a photo to user
    # await bot.send_photo(message.chat.id, photo=open('media/pics/kitten1.jpg', "rb"), caption="Котик")
    # # send a location to user
    # await bot.send_location(message.chat.id, latitude= 50.452951, longitude= 30.523853,proximity_alert_radius=60)


async def ask_location(call, state):
    """Ask an information about location"""
    language_code = await language_code_give(call, state)
    send_location, ask_for_location = await translate_text(
        language_code, ["send_location", "ask_for_location"]
    )
    markup_request = await kb.your_location(send_location)
    await call.message.answer(ask_for_location, reply_markup=markup_request)


def fifteen_days(n):
    """Return the date that is 15 days from today, excluding any specified rest days."""
    current_date = datetime.datetime.now().date()
    dates = [current_date + datetime.timedelta(days=x) for x in range(n)]
    rest_day = datetime.date(2023, 4, 16)  # example date to exclude

    for rest_day in rest_days:
        if rest_day in dates:
            dates.remove(rest_day)
    return dates


def get_date(number):
    """takes a number as an input and returns the date, based on whether the number is greater or less than the current date's day"""
    today = datetime.datetime.today()
    if number > today.day:
        return today.replace(day=number).strftime("%Y-%m-%d")
    else:
        next_month = today.replace(day=28) + datetime.timedelta(days=4)
        return next_month.replace(day=number).strftime("%Y-%m-%d")


def get_date_with_month(four_diget):
    """Makes the date from 4 digits"""
    date_string = four_diget
    year = datetime.datetime.now().year
    day = int(date_string[:2])
    month = int(date_string[2:])
    year = (
        datetime.datetime.now().year
        if month >= datetime.datetime.now().month
        else datetime.datetime.now().year + 1
    )
    date = datetime.date(year=year, month=month, day=day)
    formatted_date = date.strftime("%Y-%m-%d")
    return formatted_date


def data_formatter(day):
    """Formatted date in to standard view"""
    try:
        number = only_numbers(day)
        if len(day) < 3:
            day = get_date(int(number))
        elif len(day) >= 3:
            if len(number) == 4:
                day = get_date_with_month(number)
            elif len(number) < 3:
                day = get_date(int(number))
            else:
                return None
    except ValueError:
        return None
    return day


async def ask_for_data(obj, state):
    """Thanks for the address and ask for chose the date"""
    message = obj_processor(obj)
    language_code = await language_code_give(obj, state)
    ask_for_date = await translate_text(language_code, "ask_for_date")

    # make 15 keys
    n = 15
    dates = fifteen_days(n)
    while len(dates) < 15:
        n += 1
        dates = fifteen_days(n)

    formatted_dates = [date.strftime("%d-%m") for date in dates]
    markup_request = await kb.plural_buttons(formatted_dates, 5)
    # send message with 15 buttons of the day
    await message.answer(ask_for_date, reply_markup=markup_request)


async def day_selector(message, state):
    """hear and change the recived date in correct format save it  and ask for time"""
    # Import message text
    language_code = await language_code_give(message, state)
    incorrect_data,day_appointment = await translate_text(language_code, ("incorrect_data", "day_appointment"))

    # change Time format
    day = data_formatter(message.text)
    if not day:
        await message.answer(incorrect_data)
        await ask_for_data(message, state)
        return False
    chat_id = int(message.chat.id)
    time = await at_time(date=day, chat_id=chat_id)
    print(time)
    if time:
        await message.answer(day_appointment.format(time=time[:5]))
        await ask_for_data(message, state)
        return False
    # save time format in state
    await state.update_data(day=day)
    return True


async def ask_for_time(message, state, bot):

    # Import message text
    language_code = await language_code_give(message, state)
    ask_for_time, back = await translate_text(language_code, ("ask_for_time", "back"))
    # change Time format
    data = await state.get_data()
    day = data.get("day")
    duration = data.get("duration")
    time_addition = 30
    if data.get("address") == "salon":
        time_addition = 0

    takes_time = duration + time_addition
    busy_time = busy_time_maker(day)
    times = give_possible_time(busy_time, duration)
    # if in this day didn't fit no more appointments this size
    if times == []:
        procedure_number = data.get("procedure_number")
        chat_id = int(message.chat.id)
        now = message.date
        address = data.get("address")
        act, price, day_busy = await translate_text(
            language_code,
            [
                f"act_1_{procedure_number}",
                f"price_act_1_{procedure_number}",
                "day_busy",
            ],
        )
        if not price:
            price = data.get("total_priсe")
        # send incomplete appointment to the DB
        query = """
            INSERT INTO appointments
            (chat_id, date, procedure, duration, place, price, registration_time, phone , status)
            VALUES (?, ?, ?, ?, ?, ?, ?,(SELECT phone_number FROM users WHERE id = ?), 2)
            """
        cursor.execute(
            query,
            (chat_id, day, act, takes_time, address, int(price), now, chat_id),
        )
        conn.commit()

        row = cursor.execute(
            "SELECT phone_number, first_name, last_name FROM users WHERE id = ?;",
            (chat_id,),
        )
        row = cursor.fetchone()
        phone = row[0]
        first_name = row[1]
        last_name = row[2]
        summary = f"{first_name} {last_name}: +{phone}"
        # send message to administrator with info about incompleted appointment
        await bot.send_message(
            chat_id=specialist, text=f"Incompleted appointment for {day} \n{summary} "
        )
        # Send a message to the user informing them that there are no available appointments on that day.
        await message.answer(day_busy)
        # go to ask date again
        await ask_for_data(message, state)
        await ST.Booking.SEL_Date.set()
        return False

    formatted_times = [time.strftime("%H:%M") for time in times]
    formatted_times.append(back)
    markup_request = await kb.plural_buttons(formatted_times, 5)
    await message.answer(ask_for_time, reply_markup=markup_request)
    return True


def busy_time_maker(day):
    """Takes the appointments from Google calendar and create the dictionary with it for day"""
    busy_time = []
    # ask from google calendar events

    events = calendar.get_events(calendar_id=calendar_id, date=day)

    # from events makes the busy list
    for event in events:
        appointment = []
        start_time = event["start"]["dateTime"][11:19]
        end_time = event["end"]["dateTime"][11:19]
        appointment.append(datetime.datetime.strptime(start_time, "%H:%M:%S").time())
        appointment.append(datetime.datetime.strptime(end_time, "%H:%M:%S").time())
        if start_time != end_time:
            busy_time.append(appointment)
    # sort it
    busy_time = sorted(busy_time, key=lambda x: x[0])

    # create start if the day is today
    if datetime.datetime.now().strftime("%Y-%m-%d") == day:

        now = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%H:%M"), "%H:%M"
        ).time()

        # filtering all what is less than Now
        busy_time = list(filter(lambda x: x[1] >= now, busy_time))
        # if its empty add not in the middle of appointment
        if not busy_time or not busy_time[0][0] <= now <= busy_time[0][1]:
            busy_time.insert(0, [datetime.time.min, now])

    return busy_time


def time_formatter(text):
    """change entered text in datatime format"""
    number = only_numbers(text)
    if len(number) == 0:
        return None
    elif len(number) < 3:
        hours = number
        if "pm" in text.lower():
            hours = str(int(number) + 12)
        minutes = "00"
    elif len(number) == 3:
        hours = number[0]
        if "pm" in text.lower():
            hours = str(int(hours) + 12)
        minutes = number[-2:]
    elif len(number) == 4:
        hours = number[:2]
        minutes = number[-2:]
    elif len(number) > 4:
        return None

    if int(hours) > 24 or int(minutes) > 60:
        return None

    time_format = datetime.time(hour=int(hours), minute=int(minutes))
    return time_format


def free_time_between_appointments(busy_time):
    """Create the gap between of one appointment and begin of other"""

    # Find the gap begin from the most little end
    gap_start = datetime.time.max

    for appointment in busy_time:
        busy_end = appointment[1]
        if busy_end <= gap_start:
            gap_start = busy_end

    # Find the gap and
    gap_end = datetime.time.max

    for appointment in busy_time:
        busy_start = appointment[0]
        if busy_start >= gap_start and busy_start < gap_end:
            gap_end = busy_start

    return (gap_start, gap_end)


def gap_duration_compare(gap, duration):
    """Compare the gap and the duration, return True if it fits"""
    gap_start, gap_end = gap
    duration = datetime.timedelta(minutes=duration)
    gap = datetime.datetime.combine(
        datetime.date.today(), gap_end
    ) - datetime.datetime.combine(datetime.date.today(), gap_start)
    if duration < gap:
        return True


def available_time_slots(busy_time, duration):
    """Add function to generate available time slots based on busy times and required duration."""
    gaps = []
    # start = datetime.time.min

    while True:
        gap = free_time_between_appointments(busy_time)
        for i in range(len(busy_time)):
            if busy_time[i][1] == gap[0]:
                del busy_time[i]
                break

        if gap_duration_compare(gap, duration):
            gaps.append(gap)
        # Move to the next gap
        gap_start, gap_end = gap
        start = gap_end
        if gap_end == datetime.time.max:
            break

    return gaps


def give_possible_time(busy_time, duration):
    """return possible time for buttons"""
    gaps = available_time_slots(busy_time, duration)

    duration = datetime.timedelta(minutes=duration)

    # Generate a list of all possible times with given constraints
    hours = []
    for hour in range(0, 24):
        time = datetime.time(hour, 0)
        hours.append(time)

    times = []
    for gap in gaps:
        start_time, end_time = gap
        # add first possible time
        times.append(start_time)
        current_time = datetime.datetime.combine(datetime.date.today(), start_time)
        end_datetime = (
            datetime.datetime.combine(datetime.date.today(), end_time) - duration
        )
        # add other times with exact hours
        for hour in hours:
            if end_datetime.time() > hour > current_time.time():
                if not hour in times:
                    times.append(hour)

        if not end_datetime.time() in times:
            times.append(end_datetime.time())

    return times


def check_time_slot_fit(start_time, duration, gaps):
    """Check if time is fit in gap"""

    end_time = datetime.datetime.combine(
        datetime.date.today(), start_time
    ) + datetime.timedelta(minutes=duration)

    start_time = datetime.datetime.combine(
        datetime.date.today(), start_time
    )  # + datetime.timedelta(minutes=2)

    for gap in gaps:
        gap_start = datetime.datetime.combine(datetime.date.today(), gap[0])
        gap_end = datetime.datetime.combine(datetime.date.today(), gap[1])
        if start_time >= gap_start and end_time <= gap_end:
            # No overlap, the time slot can fit into this gap
            return True
    # No gap can fit the time slot
    return False


async def time_selector(message, state, bot):
    """hear and change the recived time in correct format save it  and ask for time"""
    # Import message text
    language_code = await language_code_give(message, state)
    incorrect_time, time_busy = await translate_text(
        language_code, ["incorrect_time", "time_busy"]
    )

    # change Time format
    time_appointment = time_formatter(message.text)

    if not time_appointment:
        await message.reply(incorrect_time)
        await ask_for_time(message, state, bot)

    # take datta from state
    data = await state.get_data()
    day = data.get("day")
    duration = data.get("duration")
    time_addition = 3
    if data.get("address") == "salon":
        time_addition = 0
    # calculate time
    duration += time_addition
    busy_time = busy_time_maker(day)
    gaps = available_time_slots(busy_time, duration)

    # check if the time for fit in gap
    if not check_time_slot_fit(time_appointment, duration, gaps):
        await message.answer(time_busy)
        # await ask_for_time(message, state)

        return False
        # time_appointment = None

    # save time format in state
    await state.update_data(time_appointment=time_appointment)
    return True


async def approve_appointment(message, state):
    """send message with approve appointment"""
    # load datas from state
    data = await state.get_data()
    day = data.get("day")
    time_appointment = data.get("time_appointment")
    try:
        time_appointment = time_appointment.strftime("%H:%M:%S")
    except AttributeError:
        return False
    procedure_number = data.get("procedure_number")
    address = data.get("address")
    specialist = data.get("specialist")
    kind = data.get("kind")
    out = data.get("out")
    duration = data.get("duration")
    price_total = data.get("price_total")
    procedure_number = data.get("procedure_number")

    # Import message text
    language_code = await language_code_give(message, state)
    (
        loc,
        act,
        price,
        time_act,
        place_out,
        coordinates,
        salon_location,
        currency,
    ) = await translate_text(
        language_code,
        [
            "loc",
            f"act_1_{procedure_number}",
            f"price_act_1_{procedure_number}",
            f"time_act_1_{procedure_number}",
            "place",
            "coordinates",
            "salon_location",
            "currency",
        ],
    )

    # calculate price
    if not price_total:
        price = only_numbers(price)

        if address == "salon":
            price_total = int(price)
        else:
            place_out = only_numbers(place_out)
            price_total = int(price) + int(place_out)

    if data.get("procedure"):
        act = data.get("procedure")

    takes_time = duration
    # add in to DB
    chat_id = int(message.chat.id)
    now = message.date
    cursor.execute(
        "INSERT INTO appointments (chat_id, date, time, procedure, duration, place, price, registration_time, procedure_number, kind) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            chat_id,
            day,
            time_appointment,
            act,
            takes_time,
            address,
            int(price_total),
            now,
            procedure_number,
            kind,
        ),
    )
    conn.commit()

    # add buttons
    approve_appointment, keyboard = await kb.two_InlineKeyboardButton(
        language_code, "approve_appointment", "yes", "change", "confirm", "book again"
    )
    if address == "salon":
        address = salon_location
    # send the message with all datas to user for prove
    await message.answer(
        f"{approve_appointment}{act}\n{day} {time_appointment}\n{loc}{address}\n{price_total}{currency}\n{str(takes_time)}",
        reply_markup=keyboard,
    )


async def create_en_event(call, state, summary):
    """Create the event with appointment"""
    # assign language code
    language_code = "en"
    # load datas from state
    data = await state.get_data()
    day = data.get("day")
    time_appointment = data.get("time_appointment")
    time_appointment = time_appointment.strftime("%H:%M:%S")
    procedure_number = data.get("procedure_number")
    address = data.get("address")
    duration = data.get("duration")
    price_total = data.get("price_total")
    act, salon, price, place_out = await translate_text(
        language_code,
        [
            f"act_1_{procedure_number}",
            "salon",
            f"price_act_1_{procedure_number}",
            "place",
        ],
    )
    # create the body for events
    first_name = call.message.chat.first_name
    last_name = call.message.chat.last_name
    # give event the color if outside
    colorId = 1
    if not price_total:
        price = int(price)

        if address == "salon":
            price_total = int(price)
            # give event the color if in salon
            colorId = 2
            address = salon
        else:
            place_out = only_numbers(place_out)
            price_total = int(price) + int(place_out)
    description = f"{act}, {price_total}"

    event = create_event_body(
        date=day,
        start_time=time_appointment,
        duration=duration,
        summary=summary,
        description=description,
        location=address,
        colorId=colorId,
    )
    # add the event in to the google calendar
    calendar.add_event(calendar_id=calendar_id, body=event)


async def test(message):
    # take phone and name number
    chat_id = message.chat.id
    row = cursor.execute(
        "SELECT phone_number, first_name, last_name FROM users WHERE id = ?;",
        (chat_id,),
    )
    row = cursor.fetchone()
    phone = row[0]
    first_name = row[1]
    last_name = row[2]
    summary = f"{first_name} {last_name}: +{phone}"
    await message.answer(summary)


async def confirm_appointment(call, state, bot):
    """send message that will be call by phone and save the approved the appointment"""

    # take phone and name number
    chat_id = call.message.chat.id
    row = cursor.execute(
        "SELECT phone_number, first_name, last_name FROM users WHERE id = ?;",
        (chat_id,),
    )
    row = cursor.fetchone()
    phone = row[0]
    first_name = row[1]
    last_name = row[2]
    summary = f"{first_name} {last_name}: +{phone}"

    await create_en_event(call, state, summary)
    # input confirm and  phone number in DB
    cursor.execute(
        "UPDATE appointments SET phone=?, status=1 WHERE id = (SELECT id FROM appointments WHERE registration_time = (SELECT MAX(registration_time) FROM appointments WHERE chat_id = ?) AND chat_id = ?);",
        (phone, chat_id, chat_id),
    )
    conn.commit()
    # create the event in Google calendar

    # sand messages

    language_code = await language_code_give(call, state)
    we_will_call, thanks = await translate_text(
        language_code, ("we_will_call", "thanks")
    )

    await call.message.answer(f"{thanks}\n{we_will_call.format(phone=str(phone))}")
    data = await state.get_data()
    day = data.get("day")
    time_appointment = data.get("time_appointment")
    #  send message about appointment
    await bot.send_message(
        chat_id=specialist, text=f"Appointment {day} {time_appointment}\n{summary} "
    )


async def help_message(message, state, language_code):
    """send message about possible options"""
    help_message = await translate_text(language_code, "help_message")
    await message.answer(help_message, reply_markup=types.ReplyKeyboardRemove())


def nearest_appointment(obj):
    """takes data for nearest appointment"""
    message = obj_processor(obj)
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    chat_id = message.chat.id

    row = cursor.execute(
        "SELECT procedure, MIN(date), time, duration, place, price, registration_time, procedure_number, kind FROM appointments WHERE date>=? AND status=1 AND chat_id=? ORDER BY time;",
        (today, chat_id),
    )
    row = cursor.fetchone()
    if row == []:
        return False

    else:
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
        ) = (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
        )
        return (
            procedure,
            date,
            time,
            duration,
            address,
            total_priсe,
            registration_time,
            procedure_number,
            kind,
        )


async def looking(obj, state, procedure, date, time, duration, address, total_priсe):
    """Send message with your appointment and add it date and time in state"""
    # add time and date in state
    await state.update_data(date=date)
    await state.update_data(time=time)
    language_code = await language_code_give(obj, state)
    message = obj_processor(obj)
    if not procedure:
        none = await translate_text(language_code, "none_appointment")
        await message.answer(none)
        return False
    appointment, keyboard = await kb.two_InlineKeyboardButton(
        language_code,
        "your_appointment",
        "cng_app",
        "look_aps",
        "chen_del",
        "look another",
    )

    if address == "salon":
        address = await translate_text(language_code, "salon_location")

    await message.answer(
        appointment.format(
            n="",
            procedure=procedure,
            date=date,
            time=time,
            duration=duration,
            place=address,
            price=total_priсe,
        ),
        reply_markup=keyboard,
    )
    return True


#
# async def looking_another(call, state):
#     """Looks for another appointments"""
#     language_code = await language_code_give(call, state)
#     today = datetime.date.today()
#     # takes the appointments from database
#     chat_id = call.message.chat.id
#     rows = cursor.execute(
#         "SELECT procedure, date, time, duration, place, price FROM appointments WHERE date>=? AND status=1 AND chat_id=? ORDER BY date, time;",
#         (today, chat_id),
#     )
#
#     rows = cursor.fetchall()
#     if rows == []:
#         none = await translate_text(language_code, "none_appointment")
#         await call.message.answer(none)
#         return False
#     else:
#         i = 1
#         for row in rows:
#             procedure, date, time, duration, place, price = (
#                 row[0],
#                 row[1],
#                 row[2],
#                 row[3],
#                 row[4],
#                 row[5],
#             )
#             # await  call.message.answer(f"{procedure, date, time, duration, place, price}")
#             your_appointment = await translate_text(language_code, "your_appointment")
#             if place == "salon":
#                 place = await translate_text(language_code, "salon_location")
#
#
#             await call.message.answer(
#                 your_appointment.format(
#                     n=i,
#                     procedure=procedure,
#                     date=date,
#                     time=time,
#                     duration=duration,
#                     place=place,
#                     price=price,
#                 ),
#             )
#             i += 1
#
#         return rows


async def looking_another(call, state):
    """Looks for another appointments"""
    language_code = await language_code_give(call, state)
    today = datetime.date.today()
    # takes the appointments from database
    chat_id = call.message.chat.id
    rows = cursor.execute(
        "SELECT procedure, date, time, duration, place, price FROM appointments WHERE date>=? AND status=1 AND chat_id=? ORDER BY date, time;",
        (today, chat_id),
    )

    rows = cursor.fetchall()
    if rows == []:
        none = await translate_text(language_code, "none_appointment")
        await call.message.answer(none)
        return False
    else:
        i = 1
        for row in rows:
            procedure, date, time, duration, place, price = (
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
            )

            your_appointment, this = await translate_text(
                language_code, ("your_appointment", "this_one")
            )

            data = {
                f"{i}": {
                    "procedure": procedure,
                    "date": date,
                    "time": time,
                    "duration": duration,
                    "place": place,
                    "price": price,
                }
            }
            await state.update_data(**data)
            datas = f"this|{i}"
            # await call.message.answer(datas)
            button = await kb.one_InlineKeyboardButton(this, datas)
            if place == "salon":
                place = await translate_text(language_code, "salon_location")
            # button= await kb.InlineKeyboardButton_plural(("Use",f"this, {procedure}, {date}, {time}, {duration}, {place}, {price}"))
            await call.message.answer(
                your_appointment.format(
                    n=i,
                    procedure=procedure,
                    date=date,
                    time=time,
                    duration=duration,
                    place=place,
                    price=price,
                ),
                reply_markup=button,
            )
            i += 1

        return rows


async def chose_appointment_to_look(call, state):
    """send proposition to chose from appointments"""
    language_code = await language_code_give(call, state)
    chose_from_appointments = await translate_text(
        language_code, "chose_from_appointments"
    )


async def change_delete(call, state):
    """gives an option to change the appointment od delete it"""
    # get text
    language_code = await language_code_give(call, state)
    change_delete, cahnge_button, no_button, del_button = await translate_text(
        language_code, ["change_delete", "cng_app", "no", "del"]
    )
    # get buttons
    markup = await kb.InlineKeyboardButton_plural(
        ((cahnge_button, "change"), (no_button, "no"), (del_button, "cancel"))
    )
    # send message
    await call.message.answer(change_delete, reply_markup=markup)


async def are_you_sure(call, state):
    """Insure at chosen option"""
    language_code = await language_code_give(call, state)
    choise = call.data
    if choise == "change":
        sure = "cng_app"
        you_sure = "you_sure_change"
    elif choise == "cancel":
        sure = "del"
        you_sure = "you_sure_delete"

    else:
        await state.finish()
        return

    question, keyboard = await kb.two_InlineKeyboardButton(
        language_code, you_sure, sure, "no", f"{choise} it", "no"
    )
    option = await translate_text(language_code, sure)
    # send message to prove the choise
    await call.message.answer(question, reply_markup=keyboard)


async def take_appointment_from_db(date, time, chat_id):
    """takes datas for appointment by date and time"""

    row = cursor.execute(
        "SELECT procedure, date, time, duration, place, price, registration_time, procedure_number, kind FROM appointments WHERE date=? AND status=1 AND chat_id=? and time=?;",
        (date, chat_id, time),
    )
    row = cursor.fetchone()
    if row == []:
        return False

    else:
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
        ) = (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
        )
        return (
            procedure,
            date,
            time,
            duration,
            address,
            total_priсe,
            registration_time,
            procedure_number,
            kind,
        )


async def change_date_appointment(call, state, bot):
    """Change date appointment"""
    data = await state.get_data()
    date = data.get("date")
    time = data.get("time")
    # find appointment in DB
    chat_id = call.message.chat.id
    # takes datas from DB
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
    ) = await take_appointment_from_db(date, time, chat_id)

    await change_status_appointment(call, date, time, status=3)
    # asking to input a new date
    await ask_for_data(call, state)
    await ST.Booking.SEL_Date.set()

    # send a datas into state
    await state.update_data(kind=kind)
    await state.update_data(address=address)
    await state.update_data(duration=duration)
    await state.update_data(procedure=procedure)
    await state.update_data(total_priсe=total_priсe)
    await state.update_data(procedure_number=procedure_number)
    await state.update_data(registration_time=registration_time)

    # Delete appointment from google calendar
    await delete_event(call, date, time, bot, reason="MOVED", colorId=8)


async def change_status_appointment(call, date, time, status):
    """change status of appointment"""
    # find appointment in DB
    chat_id = call.message.chat.id
    now = call.message.date
    cursor.execute(
        "UPDATE appointments SET status=?, changed=? WHERE date=? AND time=? AND chat_id=?",
        (status, now, date, time, chat_id),
    )
    conn.commit()


async def cancel_appointment(call, state, bot):
    """cancel the appointment"""
    # takes date and time  to find the appointment
    data = await state.get_data()
    date = data.get("date")
    time = data.get("time")
    # find appointment in DB
    chat_id = call.message.chat.id
    # takes datas from DB
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
    ) = await take_appointment_from_db(date, time, chat_id)

    await change_status_appointment(call, date, time, status=0)
    # take phone number
    phone = cursor.execute("SELECT phone_number FROM users WHERE id = ?;", (chat_id,))
    phone = cursor.fetchone()
    phone = phone[0]
    # Send message we will call you
    language_code = await language_code_give(call, state)
    we_will_call = await translate_text(language_code, "we_will_call")

    await call.message.answer(we_will_call.format(phone=str(phone)))
    # delete event from google calendar
    await delete_event(call, date, time, bot)


async def delete_event(call, date, time, bot, reason="CANCELED", colorId=11):
    # Delete appointment from google calendar
    calendar.del_event(calendar_id=calendar_id, date=date, start_time=time)

    chat_id = call.message.chat.id
    row = cursor.execute(
        "SELECT phone_number, first_name, last_name FROM users WHERE id = ?;",
        (chat_id,),
    )
    row = cursor.fetchone()
    phone = row[0]
    first_name = row[1]
    last_name = row[2]
    summary = f"{first_name} {last_name}: +{phone}"
    date_time = f"{date} {time}"
    # send message to specialist
    await bot.send_message(chat_id=specialist, text=f"{reason} {date_time}\n{summary}")
    body = create_event_body(
        date=date,
        start_time=time,
        duration=0,
        summary=reason,
        description=summary,
        location=reason,
        colorId=colorId,
    )
    # left "crumbs" from deletions or canceling
    calendar.add_event(calendar_id=calendar_id, body=body)


async def at_time(date, chat_id, kind="massage"):
    """Return time of appointment in this day to this specialist"""

    row = cursor.execute(
        "SELECT time FROM appointments WHERE date=? AND kind=? AND chat_id=? ;",
        (date, kind, chat_id),
    )

    row = cursor.fetchone()
    if row == None:
        return False
    else:
        time = row[0]

    return time
