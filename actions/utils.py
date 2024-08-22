import inspect
from datetime import datetime
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Tracker
from actions.constants import *
import logging
import mimetypes
import random
import smtplib
import traceback
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import make_msgid
import os
from pathlib import Path
from .credentials import *
import base64
import babel.dates

logger = logging.getLogger(__name__)

def get_metadata(events: List[Dict[Text, Any]]) -> Dict[Text, Any]:
    user_events = []
    for single_event in events:
        if single_event.get("event") == "user":
            user_events.append(single_event)
    return user_events[-1].get("metadata")


def get_datetime(meet_time):
    dt = datetime.fromisoformat(meet_time)
    meet_date = dt.date()
    meet_time = dt.time()
    return str(meet_date), str(meet_time)

def send_email(subject, recipient_mail, mail_type):
    try:
        message_data = EmailMessage()
        message_data["Subject"] = subject
        username = EMAIL
        password = PASS
        message_data["From"] = username
        message_data["To"] = recipient_mail
        this_path = Path(os.path.realpath(__file__))
        content = get_html_data(f"{this_path.parent}\\{mail_type}.html")
        message_data.add_alternative(content, subtype="html")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(username, password)
            smtp_server.send_message(message_data)
        return True
    except Exception as error:
        logger.error(f'Error: {error}')
        logger.info(traceback.print_exc())
        return False

def get_html_data(filepath:str):
    with open(filepath, "r") as html_data:
        return html_data.read()
    
def get_image_data(image_path):
    """
    Reads a PNG image from the given path and returns the base64 encoded data URL.

    Args:
        image_path (str): The file path to the PNG image.

    Returns:
        str: The base64 encoded data URL of the image.
    """
    try:
        with open(image_path, "rb") as image_file:
            # Read the image file and encode it in base64
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # Create a data URL for the image
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        logger.error(f"Failed to read image data from {image_path}: {e}")
        return None
    
def get_meeting_details(meeting_date, meeting_time, emails):
    logger.debug(f"{str(meeting_date), str(meeting_time), str(emails)}")
    start_time = datetime.strptime(meeting_time, "%H:%M:%S")
    end_time = start_time + timedelta(minutes=15)
    start = start_time.strftime("%H:%M")
    end = end_time.strftime("%H:%M")
    time = {
            'start': meeting_date + 'T' + start + ':00.000000',
            'end': meeting_date + 'T' + end + ':00.000000'
        }
    topic = "Demonstration of DigiSparks AI-Powered Sales Call Agent."
    guests = {email: email for email in emails}
    logger.debug(f"{time, topic, guests}")
    return  time, topic, guests


def convert_to_speakable_text(datetime_str, locale='en_US'):
    # Parse the input datetime string
    dt = datetime.strptime(datetime_str, '%Y-%m-%d at %H:%M:%S')

    # Format the date and time in a speakable way
    speakable_date = babel.dates.format_date(dt, format='full', locale=locale)
    speakable_time = babel.dates.format_time(dt, format='short', locale=locale)

    # Combine date and time into a single speakable string
    speakable_text = f"{speakable_date} at {speakable_time}"

    return speakable_text
