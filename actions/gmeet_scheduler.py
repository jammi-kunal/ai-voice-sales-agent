from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from uuid import uuid4
from typing import Dict, List
import os
import logging

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]
# CREDENTIALS_PATH = "C://Users//jammi//SalesAI//sales-rasa//actions//credentials.json"
# TOKEN_PATH = "C://Users//jammi//SalesAI//sales-rasa//actions//token.json"
CREDENTIALS_PATH = "./actions/credentials.json"
TOKEN_PATH = "./actions/token.json"



class CreateMeet:
    def __init__(self, attendees: Dict[str, str],
                 event_time: Dict[str, str], Topic):
        authe = self._auth()
        attendees_list = [{"email": e} for e in attendees.values()]
        self.event_states = self._create_event(
            attendees_list, event_time, authe, Topic)

    @staticmethod
    def _create_event(
            attendees: List[Dict[str, str]], event_time, authe: build, TopiC):
        event = {"conferenceData": {"createRequest": {"requestId": f"{uuid4().hex}", "conferenceSolutionKey": {"type": "hangoutsMeet"}}},
                 "attendees": attendees,
                 "start": {"dateTime": event_time["start"], 'timeZone': 'Asia/Kolkata'},
                 "end": {"dateTime": event_time["end"], 'timeZone': 'Asia/Kolkata'},
                 "summary": TopiC,
                 "reminders": {"useDefault": True}
                 }
        logger.error(event)
        event = authe.events().insert(calendarId="primary", sendNotifications=True,
                                      body=event, conferenceDataVersion=1).execute()
        return event

    @staticmethod
    def _auth():
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        logger.error(creds)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.error("Token exists and is expired or needs to be refreshed.")
                creds.refresh(Request())
            else:
                logger.error("Creating and Saving new token.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
                logger.error("Accessed credentials.json")
                # creds = flow.run_local_server(port=0)
                creds = flow.run_local_server(port=0)
                logger.error("creds loaded")
                # Save the credentials for the next run
                with open(TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())
                logger.error("Tokens saved")
        service = build("calendar", "v3", credentials=creds)
        return service
#
#
# print('------------------------------')
# print('-- Follow YYYY-MM-DD format --')
# print('------------------------------')
# date = input('Enter date of the meeting : ').strip()
# print('------------------------------------')
# print('-- Follow HH:MM and 24 hrs format --')
# print('------------------------------------')
# start = input('Enter starting time : ').strip()
# end = input('Enter ending time : ').strip()
# emails = list(
#     input('Enter the emails of guests separated by 1 space each : ').strip().split())
# topic = input('Enter the topic of the meeting : ')
#
# time = {
#     'start': date + 'T' + start + ':00.000000',
#     'end': date + 'T' + end + ':00.000000'
# }
# guests = {email: email for email in emails}
# meet = CreateMeet(guests, time, topic)
# keys = ['organizer', 'hangoutLink', 'summary', 'start', 'end', 'attendees']
# details = {key: meet.event_states[key] for key in keys}
# print('---------------------')
# print('-- Meeting Details --')
# print('---------------------')
# for key in keys:
#     print(key + ' : ', details[key])
