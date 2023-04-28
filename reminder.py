import datetime
import asyncio

from functions import translate_text
from memories import sql

async def reminders(bot):
    sent = []

    while True:
        # Get current time
        now = datetime.datetime.now().time()
        # Get today's date
        today = datetime.date.today()
        # find tomorrow's date
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        # convert it to string
        tomorrow = tomorrow.strftime("%Y-%m-%d")
        if datetime.time(8, 0) < now < datetime.time(20, 1):
            # Get today's appointments
            appointments = await sql.for_reminder(today)

            for appointment in appointments:
                if not appointment in sent:
                    # Get the time of the appointment
                    appointment_time = datetime.datetime.strptime(appointment[4], "%H:%M:%S").time()
                    # Calculate the reminder time (74 minutes before the appointment time)
                    reminder_time = datetime.datetime.combine(
                        datetime.date.today(), appointment_time
                    ) - datetime.timedelta(minutes=74)
                    reminder_time = reminder_time.time()

                    # Check if it's time to send the reminder
                    if appointment_time <= now < reminder_time:

                        # Translate the reminder and salon text
                        sent.append(appointment)
                        reminder, salon = await translate_text(appointment[0], ("daily_reminder", "salon"))
                        # Change the salon adress to the appointment details
                        if appointment[6] == "salon":
                            appointment = appointment[0:6] + (salon,) + appointment[7:]
                        # from telegss import bot
                        # Send the reminder message to the user
                        text_message = reminder.format(appointment=appointment)
                        await bot.send_message(chat_id=appointment[-1], text=text_message)

                        break

            # Wait for 15 minutes before checking again
            await asyncio.sleep(60 )#* 15)
        if datetime.time(19, 30)<now<datetime.time(20, 1):
            # takes tomorrow's appointments
            appointments=await sql.for_reminder(tomorrow)
            # send a message for each appointment
            for appointment in appointments:
                # Translate the reminder and salon text
                reminder, salon = await translate_text(appointment[0], ("tomorrow_reminder", "salon"))
                # Change the salon adress to the appointment details
                if appointment[6] == "salon":
                    appointment = appointment[0:6] + (salon,) + appointment[7:]
                # Send the reminder message to the user
                text_message = reminder.format(appointment=appointment)
                await bot.send_message(chat_id=appointment[-1],text=text_message)
                # add a delay to prevent spamming
                await asyncio.sleep(1)
            # sleep for 24 hours before sending the next batch of reminders
            await asyncio.sleep(24 * 60 * 60)

        else:
            # Wait for 1 hour before checking again
            if sent:
                sent = []
            await asyncio.sleep(60*60)



async def reminder_tomorow(bot):
    """Sends reminders to users about their appointments for tomorrow.
    This function runs in an infinite loop until the program is stopped."""
    print("remider_tomorow")
    while True:
        # find tomorrow's date
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        # convert it to string
        tomorrow = tomorrow.strftime("%Y-%m-%d")
        now = datetime.datetime.now().time()
        # set time to send the message
        if datetime.time(19, 30)<now<datetime.time(20, 1):
            # takes tomorrow's appointments
            appointments=await sql.for_reminder(tomorrow)
            # send a message for each appointment
            for appointment in appointments:
                # Translate the reminder and salon text
                reminder, salon = await translate_text(appointment[0], ("tomorrow_reminder", "salon"))
                # Change the salon adress to the appointment details
                if appointment[6] == "salon":
                    appointment = appointment[0:6] + (salon,) + appointment[7:]
                # Send the reminder message to the user
                text_message = reminder.format(appointment=appointment)
                await bot.send_message(chat_id=appointment[-1],text=text_message)
                # add a delay to prevent spamming
                await asyncio.sleep(1)
            # sleep for 24 hours before sending the next batch of reminders
            await asyncio.sleep(24 * 60 * 60)



async def remider_today(bot):
    """Reminds user about appointments today.
    This function runs in an infinite loop until the program is stopped."""
    sent = []
    print("remider_today")
    while True:
        # Get current time
        now = datetime.datetime.now().time()
        # Get today's date
        today = datetime.date.today()
        # Check if it's time to send the reminder

        if datetime.time(8, 0)<now<datetime.time(20, 1):
            # Get today's appointments
            appointments = await sql.for_reminder(today)

            for appointment in appointments:
                if not appointment in sent:
                    # Get the time of the appointment
                    appointment_time = datetime.datetime.strptime(appointment[4], "%H:%M:%S").time()
                    # Calculate the reminder time (74 minutes before the appointment time)
                    reminder_time = datetime.datetime.combine(
                                    datetime.date.today(), appointment_time
                                    ) - datetime.timedelta(minutes=74)
                    reminder_time=reminder_time.time()
                    # Check if it's time to send the reminder
                    if appointment_time <= now < reminder_time:
                        # Translate the reminder and salon text
                        sent.append(appointment)
                        reminder, salon = await translate_text(appointment[0], ("daily_reminder", "salon"))
                        # Change the salon adress to the appointment details
                        if appointment[6] == "salon":
                            appointment = appointment[0:6] + (salon,) + appointment[7:]
                        # from telegss import bot
                        # Send the reminder message to the user
                        text_message = reminder.format(appointment=appointment)
                        await bot.send_message(chat_id=appointment[-1],text=text_message)

                        break

            # Wait for 15 minutes before checking again
            await asyncio.sleep(60*15)
        else:
            # Wait for 1 hour before checking again
            if sent:
                sent = []
            await asyncio.sleep(60*60)


# asyncio.run(reminders())