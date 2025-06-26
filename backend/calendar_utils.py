# This file handles Google Calendar API stuff
# (Authentication, checking if a slot is free, and booking events)

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import pytz
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'primary'  # Change if using a different calendar

# Get the Google Calendar API service
# (Handles authentication and token saving)
def get_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to create Google Calendar service: {e}")
        return None

# Check if a time slot is free (returns True if free)
def is_time_slot_free(start_time: datetime, end_time: datetime, timezone: str = "UTC"):
    service = get_calendar_service()
    if not service:
        return False
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time.astimezone(pytz.UTC).isoformat(),
            timeMax=end_time.astimezone(pytz.UTC).isoformat(),
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        return len(events) == 0
    except HttpError as error:
        print(f"An error occurred: {error}")
        return False

# Book an event on the calendar
def book_event(
    summary: str,
    start_time: datetime,
    end_time: datetime,
    description: str = "",
    timezone: str = "UTC",
    recurrence: list = None,
    attendees: list = None,
    reminders: dict = None
):
    service = get_calendar_service()
    if not service:
        return None
    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.astimezone(pytz.UTC).isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time.astimezone(pytz.UTC).isoformat(),
            "timeZone": timezone,
        },
    }
    if recurrence:
        event["recurrence"] = recurrence
    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]
    if reminders:
        event["reminders"] = reminders
    try:
        event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return event_result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None 