from  __future__ import print_function
import datetime
import pprint

from googleapiclient.discovery import build
from dotenv import load_dotenv
from google.oauth2 import service_account
import os

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

    def add_event(self, calendar_id, body):
        return self.service.events().insert(calendarId=calendar_id, body=body).execute()

    def get_events_from_to(self, calendar_id, start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
        time_min = start_date.isoformat() + 'Z'  # add 'Z' for UTC time
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
        time_max = end_date.isoformat() + 'Z'
        events_result = self.service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max).execute()
        events = events_result.get('items', [])
        return events

    def get_events(self, calendar_id, date):
        start_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        end_date = start_date + datetime.timedelta(days=1)
        time_min = start_date.isoformat() + 'Z'
        time_max = end_date.isoformat() + 'Z'
        events_result = self.service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max).execute()
        events = events_result.get('items', [])
        return events


def create_event(date,start_time):
    event = {
        'summary': '{procedure} {name}',
        'location': "place",
        'description': '{phone}',
        'start': {
            'dateTime': '{date}T{start_time}-03:00',
            # 'dateTime': '2023-04-20T09:00:00-03:00',
        },
        'end': {
            'dateTime': '2023-04-20T10:00:00-03:00',

        },


        # 'reminders': {
        #     'useDefault': False,
        #     'overrides': [
        #         {'method': 'email', 'minutes': 24 * 60},
        #         {'method': 'popup', 'minutes': 10},
        #     ],
        # },
    }
    return event

calendar = GoogleCalendar()

#
# # pprint.pprint(obj.get_calendar_list())
# procedure, name, place, phone, date, start_time, end_time="go ", "Mike", "home", "4086693","2023-04-20","09:00:00", "10:00:00"
# # event=create_event(procedure, name, place, phone, date, start_time, end_time),
# event=create_event(date,start_time)
# # calendar.add_event(calendar_id=calendar_id,body=event)
# pprint.pprint(calendar.get_events(calendar_id=calendar_id, start_date="2023-04-18T07:00:00", end_date="2023-04-21T10:00:00"))
# pprint.pprint(calendar.get_events(calendar_id=calendar_id, date="2023-04-20"))
# events=[{'end': {'dateTime': '2023-04-20T16:00:00+03:00', 'timeZone': 'UTC'},
# 'start': {'dateTime': '2023-04-20T15:00:00+03:00', 'timeZone': 'UTC'}
#   }]



# events= calendar.get_events(calendar_id=calendar_id,date='2023-04-20')

#
# busy_time = {}
#
# for i, event in enumerate(events):
#     start_time = event['start']['dateTime'][11:19]
#     end_time = event['end']['dateTime'][11:19]
#     appointment = {
#         "busy_start": datetime.datetime.strptime(start_time, '%H:%M:%S').time(),
#         "busy_end": datetime.datetime.strptime(end_time, '%H:%M:%S').time()
#     }
#     busy_time[f"Appointment{i}"] = appointment
#

