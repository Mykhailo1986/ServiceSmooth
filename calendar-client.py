# from  __future__ import print_function

import datetime
import os.path
import pprint

from google.auth.transport.requests import Request

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from google.oauth2 import service_account
import os
import json

# Load environment variables from .env file
load_dotenv()
calendar_id = os.getenv('calendar_id')

class GoogleCalendar:

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    # Access environment variable
    FILE_PATH = os.getenv('CALENDAR')


    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(filename=self.FILE_PATH, scopes=self.SCOPES)
        self.service = build('calendar', 'v3', credentials=credentials)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {
            'id': calendar_id
        }

        return self.service.calendarList().insert(body=calendar_list_entry).execute()

    def add_event(self, calendar_id, event):
        event = {
            'summary': f'{rpocedure} {name}',
            'location': place,
            'description': f'{phone}',
            'start': {
                'dateTime': f'{date}T{start_time}:00-03:00',
                # 'dateTime': '2023-04-20T09:00:00-03:00',
            },
            'end': {
                'dateTime': f'{date}T{end_time}:00-03:00',
                'dateTime': '2023-04-20T17:00:00-03:00',

            },
            # 'recurrence': [
            #     'RRULE:FREQ=DAILY;COUNT=2'
            # ],

            # 'reminders': {
            #     'useDefault': False,
            #     'overrides': [
            #         {'method': 'email', 'minutes': 24 * 60},
            #         {'method': 'popup', 'minutes': 10},
            #     ],
            # },
        }
        return self.service.events().insert(calendarId=calendar_id, body=event).execute()




calendar = GoogleCalendar()


# pprint.pprint(obj.get_calendar_list())

calendar.add_event(calendar_id=calendar_id,event=event)
