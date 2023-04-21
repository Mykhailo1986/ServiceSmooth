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
        '''add event in to chosen calendar'''
        return self.service.events().insert(calendarId=calendar_id, body=body).execute()

    def get_events(self, calendar_id, date):
        '''takes event from calendar in chosen day'''
        start_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        end_date = start_date + datetime.timedelta(days=1)
        time_min = start_date.isoformat() + 'Z'
        time_max = end_date.isoformat() + 'Z'
        events_result = self.service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max).execute()
        events = events_result.get('items', [])
        return events


    def del_event(self, calendar_id, date, start_time):#, phone):
        ''' delete event from calendar'''

        for event in self.get_events(calendar_id, date):
            if event['start']['dateTime'] == f"{date}T{start_time}+03:00":
                return self.service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()

        #     events = self.get_events(calendar_id, date)
    #     for event in events:
    #         # if event['description'] == phone and event['start']['dateTime'] == f"{date}T{start_time}+03:00":
    #         if event['start']['dateTime'] == f"{date}T{start_time}+03:00":
    #             id = event['id']
    #             return self.service.events().delete(calendarId=calendar_id, eventId=id).execute()
    #
    #     return None


    def _get_events_from_to(self, calendar_id, start_date, end_date):
        '''take events with chosen dates range '''
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
        time_min = start_date.isoformat() + 'Z'  # add 'Z' for UTC time
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
        time_max = end_date.isoformat() + 'Z'
        events_result = self.service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max).execute()
        events = events_result.get('items', [])
        return events




def create_event_body(date, start_time, duration, summary, description ,location, colorId):
    '''create body for event'''
    end_time = datetime.datetime.combine(
        datetime.date.today(), start_time
    ) + datetime.timedelta(minutes=duration)
    end_date_time=f'{date}T{end_time}-03:00'
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': f'{date}T{start_time}-03:00',
            # 'dateTime': '2023-04-20T09:00:00-03:00',
        },
        'end': {
            'dateTime': end_date_time,

        },
        'colorId' : colorId,
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

# calendar.del_event(calendar_id=calendar_id,date='2023-04-20',start_time="23:00:00")
# pprint.pprint(calendar.get_events(calendar_id=calendar_id, date="2023-04-20"))

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

def create_event_body2(date, start_time, duration, summary, description ,location, colorId):
    '''create body for event'''


    end_time = datetime.datetime.strptime(start_time, "%H:%M:%S") + datetime.timedelta(minutes=duration)
    formatted_time = end_time.strftime("%H:%M:%S")
    end_date_time=f'{date}T{formatted_time}-03:00'

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': f'{date}T{start_time}-03:00',
            # 'dateTime': '2023-04-20T09:00:00-03:00',
        },
        'end': {
            'dateTime': end_date_time,
            # 'dateTime': '2023-04-20T09:00:00-03:00',
        },
        'colorId' : colorId,
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
#
# date, start_time,duration = "2023-04-20","09:00:00", 20
# event=create_event_body2(date,start_time,duration)
# calendar.add_event(calendar_id=calendar_id,body=event)

working_time = {"work_start": datetime.time(8, 0), "work_end": datetime.time(22, 0)}
def busy_time_maker(day):
    """Takes the appointments from Google calendar and create the dictionary with it for day"""
    busy_time = {}
    # ask from google calendar events
    events = calendar.get_events(calendar_id=calendar_id, date=day)
    # create start if the day is today
    if datetime.datetime.now().strftime('%Y-%m-%d') == day:
        busy_end = datetime.datetime.strptime(
            datetime.datetime.now().strftime('%H:%M'), '%H:%M'
        ).time()
    else:
        busy_end = working_time["work_start"]

    # create a busy time dictionary
    busy_time["morning"] = {
        "busy_start": datetime.time.min,
        "busy_end": busy_end,
    }

    for i, event in enumerate(events):
        start_time = event['start']['dateTime'][11:19]
        end_time = event['end']['dateTime'][11:19]
        appointment = {
            "busy_start": datetime.datetime.strptime(start_time, '%H:%M:%S').time(),
            "busy_end": datetime.datetime.strptime(end_time, '%H:%M:%S').time()
        }
        busy_time[f"Appointment{i}"] = appointment

    busy_time["night"] = {
            "busy_start": working_time["work_end"],
            "busy_end": datetime.time.max,
        }

    return busy_time

print(busy_time_maker("2023-04-21"))
