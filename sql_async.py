from dotenv import load_dotenv
import os
import aiosqlite

class SQL:
    """For working with DataBase"""
    def __init__(self, data_base_address):
        self.conn = None
        self.cursor = None
        self.data_base_address = data_base_address

    async def connect(self):
        """Create an asynchronous connection and cursor"""
        self.conn = await aiosqlite.connect(self.data_base_address)
        self.cursor = await self.conn.cursor()


    async def close(self):
        """Close the connection"""
        await self.cursor.close()
        await self.conn.close()

    async def nearest_apointment(self, today, chat_id):
        """Return (procedure, date, time, duration, address,  total_priсe,  registration_time, procedure_number, kind)
        For nearest appointment"""
        await self.connect()
        row = await self.cursor.execute(
            "SELECT procedure, MIN(date), time, duration, place, price, registration_time, procedure_number, kind FROM appointments WHERE date>=? AND status=1 AND chat_id=?;",
            (today, chat_id),
        )
        row = await self.cursor.fetchone()


        if row is None:
            return False
        else:
            (
                procedure,
                date,
                time,
                duration,
                address,
                total_price,
                registration_time,
                procedure_number,
                kind,
            ) = row
            return (
                procedure,
                date,
                time,
                duration,
                address,
                total_price,
                registration_time,
                procedure_number,
                kind,
            )


    async def all_appointments(self, chat_id, today):
        """return the list of next appointments """
        await self.connect()
        await self.cursor.execute(
            "SELECT procedure, date, time, duration, place, price FROM appointments WHERE date>=? AND status=1 AND chat_id=? ORDER BY date, time;",
            (today, chat_id),
        )
        rows = await self.cursor.fetchall()
        await self.close()
        return rows

    async def give_contact(self, chat_id):
        """Gives names and phone number"""
        await self.connect()
        await self.cursor.execute(
            "SELECT phone_number, first_name, last_name FROM users WHERE id = ?;",
            (chat_id,),
        )
        row = await self.cursor.fetchone()
        # TODO: Think about If didn't find the user
        phone = row[0]
        first_name = row[1]
        last_name = row[2]
        return first_name, last_name, phone

    async def confirm(self, chat_id, phone, day, time_appointment, kind):
        """Update status to 1 and add phone number"""
        await self.connect()
        await self.cursor.execute(
            "UPDATE appointments SET phone=?, status=1 WHERE date=? AND time=? AND chat_id=? AND kind=?",
            (phone, day, time_appointment, chat_id, kind),
        )
        await self.conn.commit()
        await self.close()

    async def create_appointment(self, act, address, chat_id, day, kind, now, price_total, procedure_number, takes_time,
                                 time_appointment):
        """Create new appointment"""
        await self.connect()
        await self.cursor.execute(
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
        await self.conn.commit()

    async def at_time(self, date, chat_id, kind="massage"):
        """Return time of appointment in this day to this specialist"""
        await self.connect()
        await self.cursor.execute(
            "SELECT time FROM appointments WHERE date=? AND kind=? AND chat_id=? ;",
            (date, kind, chat_id),
        )

        row = await self.cursor.fetchone()
        await self.close()
        if row == None:
            return None
        else:
            time = row[0]

        return time

    async def unfinished_appointment(self, act, address, chat_id, day, now, price, takes_time):
        query = """
                INSERT INTO appointments
                (chat_id, date, procedure, duration, place, price, registration_time, phone , status)
                VALUES (?, ?, ?, ?, ?, ?, ?,(SELECT phone_number FROM users WHERE id = ?), 2)
                """
        await self.connect()
        await self.cursor.execute(
            query,
            (chat_id, day, act, takes_time, address, int(price), now, chat_id),
        )
        await self.conn.commit()

    async def take_appointment_from_db(self, date, time, chat_id):
        """takes datas for appointment by date and time"""
        await self.connect()
        await self.cursor.execute(
            "SELECT procedure, date, time, duration, place, price, registration_time, procedure_number, kind FROM appointments WHERE date=? AND status=1 AND chat_id=? and time=?;",
            (date, chat_id, time),
        )
        row = await self.cursor.fetchone()
        if row == None:
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

    async def user_date(self, chat_id):
        """Returns data about the user"""
        await self.connect()
        await self.cursor.execute(
            "SELECT language_code, first_name, last_name, phone_number, email FROM users WHERE id = ?;",
            (chat_id,),
        )
        language_code, first_name, last_name, phone_number, email = await self.cursor.fetchone()

        return email, first_name, language_code, last_name, phone_number

    async def change_status(self,chat_id, date, now, status, time):
        """Change status in selected appointment"""
        await self.connect()
        await self.cursor.execute(
            "UPDATE appointments SET status=?, changed=? WHERE date=? AND time=? AND chat_id=?",
            (status, now, date, time, chat_id),
        )
        await self.conn.commit()

    async def save_user(self, email, first_name, id, last_name, phone_number):
        """Save the users datas"""
        await self.connect()
        await self.cursor.execute(
            "UPDATE users SET first_name=?, last_name=?, phone_number=?, email=? WHERE id=?;",
            (first_name, last_name, phone_number, email, id),
        )
        await self.conn.commit()
        await self.close()

    async def give_users_name(self, chat_id):
        """return users name"""
        await self.connect()
        await self.cursor.execute("SELECT first_name FROM users WHERE id = ?;", (chat_id,))
        result = await self.cursor.fetchone()
        return result, None

    async def save_language_code(self, chat_id, language_code):
        await self.connect()
        await self.cursor.execute(
            "UPDATE users SET language_code = ? WHERE id = ?;", (language_code, chat_id)
        )
        await self.conn.commit()

    async def existance_check(self, chat_id, now):
        """Check if the private chat is already exist, and add it if not."""
        await self.connect()
        await self.cursor.execute("SELECT id FROM users WHERE id = ?;", (chat_id,))
        check = await self.cursor.fetchone()
        if check == None :
            await self.cursor.execute(
                "INSERT INTO users (id, registration_time) VALUES (?, ?);",
                (chat_id, now),
            )
            await self.conn.commit()

    async def language_coge_db(self, chat_id):
        """Check whether a user has already set a default language preference in the bot or not."""
        await self.connect()
        await self.cursor.execute("SELECT language_code FROM users WHERE id = ?;", (chat_id,))
        result = await self.cursor.fetchone()
        return result[0] if result else None

    async def phone_number(self, chat_id):
        await self.connect()
        await self.cursor.execute("SELECT phone_number FROM users WHERE id = ?;", (chat_id,))
        phone = await self.cursor.fetchone()
        phone = phone[0]
        return phone

    async def for_reminder(self,date):
        query = """SELECT users.language_code, users.first_name, users.last_name,  appointments.procedure, appointments.time, appointments.duration, appointments.place, appointments.price, appointments.chat_id
                    FROM appointments 
                    INNER JOIN users 
                    ON appointments.chat_id = users.id 
                    WHERE appointments.date = ? AND appointments.status = 1
                    ORDER BY appointments.time;
                """
        await self.connect()
        await self.cursor.execute(query,(date,))
        appointments = await self.cursor.fetchall()
        return appointments


load_dotenv()
sql=SQL(os.getenv("DB"))