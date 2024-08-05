from typing import Any, Text, Dict, List
from .constants import *
from .utils import *
import logging
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, SlotSet, ActiveLoop, Restarted
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.types import DomainDict
from .gmeet_scheduler import *


logger = logging.getLogger(__name__)

class ActionGreet(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        metadata = get_metadata(tracker.events)
        prospect_name = metadata.get(PROSPECT_NAME, None)
        prospect_email = metadata.get("prospect_email", None)
        prospect_name = "John"
        prospect_email = "jammikunal0@gmail.com"
        if prospect_name:
            dispatcher.utter_message(response="utter_greet", prospect_name = prospect_name, bot_name = BOT_NAME)
        else:
            dispatcher.utter_message(text="Hey! My name is Dee, I am calling you from Digisparks. If you can spare 60 seconds, I can tell you how I can make your life much easier.")
        return [SlotSet(PROSPECT_NAME, prospect_name), 
                SlotSet("prospect_email", prospect_email)]


class ActionExplain(Action):

    def name(self) -> Text:
        return "action_explain"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_explain")
        return []


class ActionRestart(Action):
    def name(self) -> Text:
        return "action_restart"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Restarted...")
        return [ActiveLoop(None), Restarted()]


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Fallback...")
        return []


class ActionAskDateTime(Action):
    def name(self) -> Text:
        return "action_ask_date_time"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_ask_availability")
        # return [SlotSet(MEETING_DATE, "27/06/2024"), SlotSet(MEETING_TIME, "18:30")]
        return []
    

class ActionAskConfirmDateTime(Action):
    def name(self) -> Text:
        return "action_ask_confirm_date_time"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        meeting_time = tracker.get_slot(MEETING_TIME)
        logger.error(f"{meeting_time}")
        meeting_date, meeting_time = get_datetime(meeting_time)
        logger.error(f"{meeting_date}, {meeting_time}")
        dispatcher.utter_message(response="utter_confirm_meeting_details", 
                                 meeting_date = meeting_date, 
                                 meeting_time = meeting_time)
        
        return [SlotSet(MEETING_DATE, meeting_date), SlotSet(MEETING_TIME, meeting_time)]


class ActionSubmitScheduleCallForm(Action):
    def name(self) -> Text:
        return "action_submit_schedule_call_form"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        meeting_date = tracker.get_slot(MEETING_DATE)
        meeting_time = tracker.get_slot(MEETING_TIME)
        prospect_name = tracker.get_slot(PROSPECT_NAME)
        prospect_email = tracker.get_slot("prospect_email")
        dispatcher.utter_message(response="utter_schedule_call_thank_you", 
                                 meeting_date = meeting_date, 
                                 meeting_time = meeting_time, 
                                 prospect_name = prospect_name)
        time, topic, guests = get_meeting_details(meeting_date, meeting_time, [prospect_email, "jammikunal000@gmail.com"])
        meet = CreateMeet(guests, time, topic)
        keys = ['organizer', 'hangoutLink', 'summary', 'start', 'end', 'attendees']
        details = {key: meet.event_states[key] for key in keys}
        for key in keys:
            logger.debug(f"Scheduled Meet Details : {key + ' : ', details[key]}")
        return []


class ActionAskRedirectionToProspect(Action):
    def name(self) -> Text:
        return "action_ask_redirection_to_prospect"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_not_the_right_person")
        return []


class ActionSubmitRedirectionForm(Action):
    def name(self) -> Text:
        return "action_submit_redirection_form"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        redirection = tracker.get_slot("redirection_to_prospect")
        if redirection == "yes":
            dispatcher.utter_message(text="Awesome! Sent you an email with a google form attached to it. Please fill out the necessary details.")
            subject = "Help Us Connect with the Right Person at Your Company"
            recipient_mail = tracker.get_slot("prospect_email")
            mail_type = "redirection_form"
            is_sent = send_email(subject, recipient_mail, mail_type)
            logger.error(f"Mail status: {is_sent}")
        else:
            dispatcher.utter_message(response="utter_redirection_form_no_response")
        return []


class ActionSilenceDetected(Action):
    def name(self) -> Text:
        return "action_silence_detected"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Sorry, I couldn't hear you. Is your network okay?")
        return []


class ActionNegativeIntentRouter(Action):
    def name(self) -> Text:
        return "action_negative_intent_router"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_intent = tracker.get_intent_of_latest_message()
        logger.debug(user_intent)
        if user_intent == DENY:
            dispatcher.utter_message(response="utter_not_interested")
        if user_intent == "ask_if_robot":
            dispatcher.utter_message(response="utter_ask_if_robot", bot_name=BOT_NAME)
        # elif user_intent == NOT_THE_RIGHT_PERSON:
        #     return [FollowupAction("action_ask_redirection_to_prospect")]
        else:
            dispatcher.utter_message(response=f"utter_{user_intent}")
        return []