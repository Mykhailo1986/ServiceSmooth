from aiogram import types
import re
import json
import keyboards as kb
import sqlite3
import datetime
import states as ST

# Connect to the database
conn = sqlite3.connect("ss.db")
cursor = conn.cursor()
# from datetime import datetime

working_time = {"work_start": datetime.time(8, 0), "work_end": datetime.time(18, 0)}


"""FOR MAX procedure search for n=5
    look in procedure_chosen in telegrass.py
    and look in text.json FROM line "act_1_1" ... TO line "time_act_1_5"
"""
"""confirm:
None = not ended 
 1 = correct agried with user
 2 = not fit in time
 3 = changed
 0 = cancelled
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


def only_numbers(text_with_nombers):
    """Extract only the numbers from a string"""
    numbers = re.findall("\d+", text_with_nombers)
    phone_number = "".join(numbers)
    return phone_number


def obj_processor(obj):
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
    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
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

    await message.answer(reg_text, reply_markup=markup_request)


async def ask_email(message, state):
    """Ask for email"""
    language_code = await language_code_from_state(state)
    ask_for_email = await translate_text(language_code, "ask_for_email")
    await message.answer(ask_for_email)


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


async def thanks(obj):
    """Send thanks"""
    # Takes a language from state
    message = obj_processor(obj)
    chat_id = int(message.chat.id)
    language_code = await language_coge_from_DB(chat_id)
    thanks = await translate_text(language_code, "thanks")
    await message.answer(thanks)


async def end_reregistration(call, state):
    language_code = await language_code_give(call, state)
    end_reg = await translate_text(language_code, "end_reg")
    key = await kb.one_button("/book")
    await call.message.answer(end_reg, reply_markup=key)


async def registration_booking(message, language_code):
    await send_registration_confirmation_message(message)
    go_reg = await translate_text(language_code, "go_reg")
    await message.answer(go_reg)


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
    """Send the message options"""
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
                f"{i} "
                + text[language_code][f"act_1_{i}"]
                + "\t"
                + text[language_code][f"time_act_1_{i}"]
                + text[language_code][f"min"]
                + "\t"
                + text[language_code][f"price_act_1_{i}"]
                + text[language_code][f"currency"]
                + "\n\n"
            )
            keys.append(f"{i}")
    keyboard = await kb.plural_buttons(keys)
    await message.answer(propose, reply_markup=keyboard)


async def save_chosen_procedure(message, state, language_code):
    """Saves the chosen procedure and it duration into the state"""
    # take a number of procedure
    procedure_number = message.text[0]
    # save it into state
    await state.update_data(procedure_number=procedure_number)
    # takes phrases in default language
    description = f"act_1_{procedure_number}_descr"
    you_chose, description, duration = await translate_text(
        language_code, ["you_chose", description, f"time_act_1_{procedure_number}"]
    )

    duration = only_numbers(duration)
    await state.update_data(duration=int(duration))
    # send message with chosen procedure
    await message.answer(f"{you_chose}: {message.text}")
    # send message with description of procedure
    await message.answer(description)


async def ask_for_location(message, language_code):
    """Propse to chose a place"""
    place, keyboard = await kb.two_InlineKeyboardButton(
        language_code,
        "place",
        "salon",
        "my_place",
        "salon",
        "my_place",
    )
    await message.answer(place, reply_markup=keyboard)


async def our_contact(bot, obj, state):
    """give an information about location of salon and save choise in state"""
    language_code = await language_code_from_state(state)
    message = obj_processor(obj)
    # send a message to user
    salon_location = await translate_text(language_code, "salon_location")
    # send a place into state
    await state.update_data(address=salon_location, time_addition=0, out=0)
    await message.answer(salon_location)
    # # send a photo to user
    # await bot.send_photo(message.chat.id, photo=open('media/pics/kitten1.jpg', "rb"), caption="Котик")
    # # send a location to user
    # await bot.send_location(message.chat.id, latitude= 50.452951, longitude= 30.523853,proximity_alert_radius=60)


async def ask_location(call, state):
    """Ask an information about location"""
    language_code = await language_code_from_state(state)
    send_location, ask_for_location = await translate_text(
        language_code, ["send_location", "ask_for_location"]
    )
    markup_request = await kb.your_location(send_location)
    await call.message.answer(ask_for_location, reply_markup=markup_request)


def fifteen_days(n):
    """Return 15 days from todey exept rest_days"""
    current_date = datetime.datetime.now().date()
    dates = [current_date + datetime.timedelta(days=x) for x in range(n)]
    # rest_day = datetime.date(2023, 4, 16)  # example date to exclude
    rest_days = [datetime.date(2023, 4, 16), datetime.date(2023, 4, 17)]
    for rest_day in rest_days:
        if rest_day in dates:
            dates.remove(rest_day)
    return dates


def get_date(number):
    """takes a number as an input and returns a date based on whether the number is greater or less than the current date's day"""
    today = datetime.datetime.today()
    if number > today.day:
        return today.replace(day=number).strftime("%d-%m-%Y")
    else:
        next_month = today.replace(day=28) + datetime.timedelta(days=4)
        return next_month.replace(day=number).strftime("%d-%m-%Y")


def get_date_with_month(four_diget):
    # Makes from 4 digits the data
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
    formatted_date = date.strftime("%d-%m-%Y")
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
    language_code = await language_code_from_state(state)
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
    language_code = await language_code_from_state(state)
    incorrect_data = await translate_text(language_code, "incorrect_data")
    # change Time format
    day = data_formatter(message.text)
    if not day:
        await message.reply(incorrect_data)
        await ask_for_data(message, state)
        return None
    # save time format in state
    await state.update_data(day=day)


async def ask_for_time(message, state):
    # Import message text
    language_code = await language_code_from_state(state)
    ask_for_time = await translate_text(language_code, "ask_for_time")
    # change Time format
    data = await state.get_data()
    day = data.get("day")
    duration = data.get("duration")
    time_addition = data.get("time_addition")
    takes_time = duration + time_addition
    busy_time = busy_time_maker(day)
    times = give_possible_time(busy_time, duration)
    # if in this day didnt fit any more appointments this size
    if times == []:
        procedure_number = data.get("procedure_number")
        chat_id = int(message.chat.id)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        address = data.get("address")
        act, price, day_busy = await translate_text(
            language_code,
            [
                f"act_1_{procedure_number}",
                f"price_act_1_{procedure_number}",
                "day_busy",
            ],
        )
        query = """
            INSERT INTO appointments
            (chat_id, date, procedure, duration, place, price, registration_time, phone , confirm)
            VALUES (?, ?, ?, ?, ?, ?, ?,(SELECT phone_number FROM users WHERE id = ?), 2)
            """
        cursor.execute(
            query,
            (chat_id, day, act, takes_time, address, int(price), now, chat_id),
        )
        conn.commit()
        await message.answer(day_busy)
        await ask_for_data(message, state)
        await ST.Booking.SEL_Date.set()
        return False

    formatted_times = [time.strftime("%H:%M") for time in times]
    markup_request = await kb.plural_buttons(formatted_times, 5)
    await message.answer(ask_for_time, reply_markup=markup_request)
    return True


def busy_time_maker(day):
    """Takes the appointments from DB and create the dictionary with it for day"""
    busy_time = {}

    rows = cursor.execute(
        "SELECT time, duration FROM appointments WHERE date=? AND confirm=1 ORDER BY time;",
        (day,),
    )
    rows = cursor.fetchall()

    if datetime.datetime.now().strftime("%d-%m-%Y") == day:
        busy_end = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%H:%M"), "%H:%M"
        ).time()
    else:
        busy_end = working_time["work_start"]

    busy_time["morning"] = {
        "busy_start": datetime.time.min,
        "busy_end": busy_end,
    }

    for i, row in enumerate(rows):
        appointment = {
            "busy_start": datetime.datetime.strptime(row[0], "%H:%M").time(),
            "busy_end": (
                datetime.datetime.strptime(row[0], "%H:%M")
                + datetime.timedelta(minutes=row[1] + 15)
            ).time(),
        }
        busy_time[f"Appointment{i}"] = appointment

    busy_time["night"] = {
        "busy_start": working_time["work_end"],
        "busy_end": datetime.time.max,
    }

    return busy_time


def time_formatter(text):
    """make inputed text in datatime format"""
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


def free_time_between_appointments(busy_time, start):
    """Create the gap between of one appointment and begin of other"""

    # Find the gap begin
    gap_start = datetime.time.max
    for key in busy_time.keys():
        busy_end = busy_time[key]["busy_end"]
        if busy_end < gap_start and busy_end > start:
            gap_start = busy_end
    # Find the gap and
    gap_end = datetime.time.max
    for key in busy_time.keys():
        busy_start = busy_time[key]["busy_start"]
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
    start = busy_time["morning"]["busy_end"]

    while True:
        gap = free_time_between_appointments(busy_time, start)
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
        while current_time <= end_datetime - datetime.timedelta(minutes=15):
            current_time += datetime.timedelta(minutes=15)
            if current_time.time() in hours:
                times.append(current_time.time())
        # add last possible time
        if not end_datetime.time() in times:
            times.append(end_datetime.time())
    return times


def check_time_slot_fit(start_time, duration, gaps):
    """Check if time is fit in gap"""
    end_time = datetime.datetime.combine(
        datetime.date.today(), start_time
    ) + datetime.timedelta(minutes=duration)
    start_time = datetime.datetime.combine(datetime.date.today(), start_time)
    for gap in gaps:
        gap_start = datetime.datetime.combine(datetime.date.today(), gap[0])
        gap_end = datetime.datetime.combine(datetime.date.today(), gap[1])
        if start_time >= gap_start and end_time <= gap_end:
            # No overlap, the time slot can fit into this gap
            return True
    # No gap can fit the time slot
    return False


async def time_selector(message, state):
    """hear and change the recived time in correct format save it  and ask for time"""
    # Import message text
    language_code = await language_code_from_state(state)
    incorrect_time = await translate_text(language_code, "incorrect_time")
    # change Time format
    time_appointment = time_formatter(message.text)

    if not time_appointment:
        await message.reply(incorrect_time)
        await ask_for_time(message, state)

    # take datta from state
    data = await state.get_data()
    day = data.get("day")
    duration = data.get("duration")
    time_addition = data.get("time_addition")
    # calculate time
    duration += time_addition
    busy_time = busy_time_maker(day)
    gaps = available_time_slots(busy_time, duration)
    # check if the time for fit in gap
    if not check_time_slot_fit(time_appointment, duration, gaps):
        await message.answer("Виберыть ынший час")
        await ask_for_time(message, state)
        time_appointment = None

    # save time format in state
    await state.update_data(time_appointment=time_appointment)


async def approve_appointment(message, state):
    """send message with approve appointment"""
    # load datas from sate
    data = await state.get_data()
    day = data.get("day")
    time_appointment = data.get("time_appointment")
    try:
        time_appointment = time_appointment.strftime("%H:%M")
    except AttributeError:
        return False
    procedure_number = data.get("procedure_number")
    address = data.get("address")
    place = data.get("place")
    specialist = data.get("specialist")
    kind = data.get("kind")
    out = data.get("out")
    duration = data.get("duration")
    # time_addition it's time to get in to the place what client chose
    time_addition = data.get("time_addition")

    # Import message text
    language_code = await language_code_from_state(state)
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
    price = only_numbers(price)
    place_out = only_numbers(place_out)
    price_total = int(price) + int(place_out) * out
    if not price_total:
        price_total = data.get("price_total")
    if data.get("procedure"):
        act = data.get("procedure")
    # calculate time
    takes_time = duration + time_addition

    chat_id = int(message.chat.id)
    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

    cursor.execute(
        "INSERT INTO appointments (chat_id, date, time, procedure, duration, place, price, registration_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            chat_id,
            day,
            time_appointment,
            act,
            takes_time,
            address,
            int(price_total),
            now,
        ),
    )
    conn.commit()

    # add buttons
    approve_appointment, keyboard = await kb.two_InlineKeyboardButton(
        language_code, "approve_appointment", "yes", "change", "confirm", "book again"
    )
    await message.answer(
        f"{approve_appointment}{act}\n{day} {time_appointment}\n{loc}{address}\n{price}{currency}\n{str(takes_time)}",
        reply_markup=keyboard,
    )


async def confirm_appointment(call, state):
    """send message that will be call by phone and save the approved the appointment"""
    # work with SQL
    # take phone number
    chat_id = call.message.chat.id
    phone = cursor.execute("SELECT phone_number FROM users WHERE id = ?;", (chat_id,))
    phone = cursor.fetchone()
    phone = phone[0]
    # input confirm and  phone number in DB
    cursor.execute(
        "UPDATE appointments SET phone=?, confirm=1 WHERE id = (SELECT id FROM appointments WHERE registration_time = (SELECT MAX(registration_time) FROM appointments WHERE chat_id = ?) AND chat_id = ?);",
        (phone, chat_id, chat_id),
    )
    conn.commit()

    # sand messages
    await thanks(call)
    language_code = await language_code_give(call, state)
    we_will_call = await translate_text(language_code, "we_will_call")
    await call.message.answer(we_will_call.format(phone=str(phone)))


async def help_message(message, state, lenguage_code):
    """send message about possible options"""
    help_message = await translate_text(lenguage_code, "help_message")
    await message.answer(help_message)


async def nearest_appointment(obj):
    """takes datta for nearest appointment"""
    message = obj_processor(obj)
    now = datetime.datetime.now().strftime("%d-%m-%Y")
    chat_id = message.chat.id
    row = cursor.execute(
        "SELECT procedure, MIN(date), time, duration, place, price FROM appointments WHERE date<=? AND confirm=1 AND chat_id=?;",
        (now, chat_id),
    )
    row = cursor.fetchone()

    if row == []:
        return False
    else:
        procedure, date, time, duration, place, price = (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
        )
        return procedure, date, time, duration, place, price


async def valid_appointments(message, state):
    """For multiply appointments"""
    now = datetime.datetime.now().strftime("%d-%m-%Y")
    chat_id = message.chat.id
    rows = cursor.execute(
        "SELECT procedure, date, time, duration, place, price FROM appointments WHERE date>=? AND confirm=1 AND chat_id=? ORDER BY time;",
        (now, chat_id),
    )
    rows = cursor.fetchall()
    if rows == []:
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
            await message.answer(
                f"Your appintment {i}:\n{procedure}, {date}, {time}, {duration}, {place}, {price} "
            )
            i += 1
        return True


async def looking(language_code, message, state):
    """Send message with your appointment"""
    procedure, date, time, duration, place, price = await nearest_appointment(message)

    if not procedure:
        await message.answer("у вас нет записи")
        return False
    appointment, keyboard = await kb.two_InlineKeyboardButton(
        language_code, "your_appointment", "cng_app", "del", "change", "cancel"
    )
    await message.answer(
        appointment.format(
            procedure=procedure,
            date=date,
            time=time,
            duration=duration,
            place=place,
            price=price,
        ),
        reply_markup=keyboard,
    )
    return True


async def are_you_sure(call, state):
    """Insure at chosen option"""
    choise = call.data
    if choise == "change":
        sure = "cng_app"
    elif choise == "cancel":
        sure = "del"
    else:
        await state.finish()
        return

    language_code = await language_code_give(call, state)
    question, keyboard = await kb.two_InlineKeyboardButton(
        language_code, "you_sure", sure, "no", f"{choise} it", "no"
    )

    await call.message.answer(question.format(choise=choise), reply_markup=keyboard)


async def change_date_appointment(call, state):
    procedure, date, time, duration, place, price = await nearest_appointment(call)
    chat_id = call.message.chat.id
    cursor.execute(
        "UPDATE appointments SET  confirm=3 WHERE date = ? time = ? AND chat_id = ?);",
        (date, time, chat_id),
    )
    conn.commit()

    await ask_for_data(call, state)
    await ST.Booking.SEL_Date.set()

    # send a datas into state
    await state.update_data(procedure=procedure)
    await state.update_data(duration=duration)
    await state.update_data(place=place)
    await state.update_data(price=price)


async def cancel_appointment(call, state):
    """cancel the appointment"""
    procedure, date, time, duration, place, price = nearest_appointment(call)
    chat_id = call.message.chat.id
    cursor.execute(
        "UPDATE appointments SET  confirm=0 WHERE date = ? time = ? AND chat_id = ?);",
        (date, time, chat_id),
    )
    conn.commit()

    # take phone number
    phone = cursor.execute("SELECT phone_number FROM users WHERE id = ?;", (chat_id,))
    phone = cursor.fetchone()
    phone = phone[0]
    # Send message we will call you
    language_code = await language_code_give(call, state)
    we_will_call = await translate_text(language_code, "we_will_call")
    await call.message.answer(we_will_call.format(phone=str(phone)))


# busy_time_maker('23-04-2023')
#
#     # Calculate the start time for the next available slot
#     start_time = datetime.datetime.combine(datetime.date.today(), last_busy_end) + datetime.timedelta(minutes=duration)
#
#     # Create a list of available time slots
#     available_times = []
#     for hour in range(start_time.hour, 24):
#         start = datetime.datetime.combine(datetime.date.today(), datetime.time(hour=hour, minute=0, second=0))
#         end = start + datetime.timedelta(minutes=duration)
#         overlaps = False
#         for key in busy_time.keys():
#             busy_start = busy_time[key]["busy_start"]
#             busy_end = busy_time[key]["busy_end"]
#             busy_range = (busy_start, busy_end)
#             slot_range = (start.time(), end.time())
#             if overlap(busy_range, slot_range):
#                 overlaps = True
#                 break
#         if not overlaps and end.time() <= busy_start:
#             available_times.append((start.time(), end.time()))
#
#     return available_times
#
#
# # Helper function to check if two time ranges overlap
# def overlap(range1, range2):
#     return not (range1[1] <= range2[0] or range2[1] <= range1[0])


# get_available_times(busy_time, duration)

# async def time_selector(message,state):
#
#     '''change the recived date in correct format save it  and ask for time '''
#     # Import message text
#     language_code = await language_code_from_state(state)
#     incorrect_data, ask_for_time = await translate_text(
#         language_code, ["incorrect_data", "ask_for_time"])
#     # change Time format
#
#     time= time_formatter(message.text)
#     if not day:
#             await message.reply(incorrect_data)
#             await ask_for_data(message, state)
#             return None
#     # save time format in state
#     await state.update_data(day=day)
#     await message.answer(ask_for_time)

# async def go_ask_for_location(message, state):
#     '''create message that "No option has been selected." and go to chose an place'''
#     # take the language code
#     language_code = await language_code_give(message, state)
#     # sand the message that nothing chosen
#     no_choice = await translate_text(language_code,"no_choice")
#     await message.answer(no_choice)
#     await ask_for_location(message, language_code)
#


# async def agree_registration_in_booking(mesage,sate)
#     language_code = await language_code_from_state()
# async def correct_registration(obj):
#     if isinstance(obj, types.Message):
#         chat_id = int(obj.chat.id)
#         message = obj
#     elif isinstance(obj, types.CallbackQuery):
#         chat_id = int(obj.message.chat.id)
#         call = obj
#         message = obj.message
#     language_code = await languageCoge_check(chat_id)
#
#     keyboard = await kb.plusural_button(["hello","/start","win"])
#
#     await message.answer("question", reply_markup=keyboard)


async def exit(obj, state):
    message = obj_processor(obj)
    language_code = await language_code_give(message, state)
    exit = await translate_text(language_code, "exit")
    await message.answer(exit)
    await state.finish()


async def exit_button():
    """Create a keyboard with one button"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(types.KeyboardButton("/exit"))
    return keyboard
