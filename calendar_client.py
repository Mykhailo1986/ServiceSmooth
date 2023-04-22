from __future__ import print_function
import datetime
import pprint

from googleapiclient.discovery import build
from dotenv import load_dotenv
from google.oauth2 import service_account
import os

# Load environment variables from .env file
load_dotenv()
calendar_id = os.getenv("calendar_id")


class GoogleCalendar:

    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    # Access environment variable
    FILE_PATH = os.getenv("CALENDAR")

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            filename=self.FILE_PATH, scopes=self.SCOPES
        )
        self.service = build("calendar", "v3", credentials=credentials)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {"id": calendar_id}

        return self.service.calendarList().insert(body=calendar_list_entry).execute()

    def add_event(self, calendar_id, body):
        """add event in to chosen calendar"""
        return self.service.events().insert(calendarId=calendar_id, body=body).execute()

    def get_events(self, calendar_id, date):
        """takes event from calendar in chosen day"""
        start_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + datetime.timedelta(days=1)
        time_min = start_date.isoformat() + "Z"
        time_max = end_date.isoformat() + "Z"
        events_result = (
            self.service.events()
            .list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max)
            .execute()
        )
        events = events_result.get("items", [])
        return events

    def del_event(self, calendar_id, date, start_time):  # , phone):
        """delete event from calendar"""

        for event in self.get_events(calendar_id, date):
            if event["start"]["dateTime"] == f"{date}T{start_time}+03:00":
                return (
                    self.service.events()
                    .delete(calendarId=calendar_id, eventId=event["id"])
                    .execute()
                )

        #     events = self.get_events(calendar_id, date)

    #     for event in events:
    #         # if event['description'] == phone and event['start']['dateTime'] == f"{date}T{start_time}+03:00":
    #         if event['start']['dateTime'] == f"{date}T{start_time}+03:00":
    #             id = event['id']
    #             return self.service.events().delete(calendarId=calendar_id, eventId=id).execute()
    #
    #     return None

    def _get_events_from_to(self, calendar_id, start_date, end_date):
        """take events with chosen dates range"""
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
        time_min = start_date.isoformat() + "Z"  # add 'Z' for UTC time
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
        time_max = end_date.isoformat() + "Z"
        events_result = (
            self.service.events()
            .list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max)
            .execute()
        )
        events = events_result.get("items", [])
        return events

    def _get_all_events(self, date):
        """get all events from all calendars"""
        calendar_list = self.service.calendarList().list().execute()
        all_events = []
        for calendar in calendar_list["items"]:
            events = self.get_events(calendar["id"], date)
            all_events.extend(events)
        return all_events


def create_event_body(
    date, start_time, duration, summary, description, location, colorId
):
    """create body for event"""

    end_time = datetime.datetime.strptime(start_time, "%H:%M:%S") + datetime.timedelta(
        minutes=duration
    )
    formatted_time = end_time.strftime("%H:%M:%S")
    end_date_time = f"{date}T{formatted_time}"
    print(date)
    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": f"{date}T{start_time}",
            "timeZone": "Europe/Kiev",
        },
        "end": {
            "dateTime": end_date_time,
            "timeZone": "Europe/Kiev",
        },
        "colorId": colorId,
        # "1" - Blue
        # "2" - Green
        # "3" - Purple
        # "4" - Red
        # "5" - Yellow
        # "6" - Orange
        # "7" - Turquoise
        # "8" - Gray
        # "9" - Bold    Blue
        # "10" - Bold    Green
        # "11" - Bold    Red
        # "12" - Bold    Yellow
        # "13" - Bold    Orange
        # "14" - Bold    Turquoise
        # "15" - Bold    Purple
        # "16" - Gray
        # "17" - Slate
        # "18" - Red    Orange
        # "19" - Brown
        # "20" - Plum
        # 'id' : '',
        # 'reminders': {
        #     'useDefault': False,
        #     'overrides': [
        #         {'method': 'email', 'minutes': 24 * 60},
        #         {'method': 'popup', 'minutes': 10},
        #     ],
        #  },
    }

    return event


calendar = GoogleCalendar()
