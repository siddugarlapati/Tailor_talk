import re
from datetime import datetime, timedelta
from calendar_utils import is_time_slot_free, book_event
import os
import openai
# from langgraph import Graph, State (Assume LangGraph is available for state management)

# This class keeps track of the conversation state
class ConversationState:
    def __init__(self):
        self.intent = None
        self.date = None
        self.hour = None
        self.minute = None
        self.confirmed = False
        self.last_prompt = None

# Try to get a date from the user's message
def parse_date(text):
    text = text.lower()
    now = datetime.now()
    if "tomorrow" in text:
        return now + timedelta(days=1)
    if "today" in text:
        return now
    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    for i, day in enumerate(days):
        if f"next {day}" in text:
            days_ahead = (i - now.weekday() + 7) % 7 + 7
            return now + timedelta(days=days_ahead)
        if f"this {day}" in text or day in text:
            days_ahead = (i - now.weekday() + 7) % 7
            return now + timedelta(days=days_ahead)
    match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    return None

# Try to get a time from the user's message
def parse_time(text):
    text = text.lower()
    if "afternoon" in text:
        return 15, 0  # 3:00 PM
    if "morning" in text:
        return 9, 0   # 9:00 AM
    if "evening" in text:
        return 18, 0  # 6:00 PM
    if "noon" in text:
        return 12, 0  # 12:00 PM
    match = re.search(r"(\d{1,2}):(\d{2}) ?(am|pm)?", text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        if match.group(3) == "pm" and hour < 12:
            hour += 12
        return hour, minute
    match = re.search(r"(\d{1,2})(am|pm)", text)
    if match:
        hour = int(match.group(1))
        if match.group(2) == "pm" and hour < 12:
            hour += 12
        return hour, 0
    return None, None

# Try to figure out what the user wants to do
def parse_intent(text):
    text = text.lower()
    if any(word in text for word in ["book", "schedule", "set up", "make an appointment"]):
        return "book"
    elif any(word in text for word in ["free", "available", "availability", "slots"]):
        return "check"
    return None

# If the user asks a general question, try to answer it with OpenAI
# (if the API key is set)
def answer_general_question(user_message):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        return "General question answering is not available (OpenAI API key not set)."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't answer that right now. ({e})"

# This will keep the state for the current session (not for production)
conversation_state = ConversationState()

def conversational_agent(user_message):
    global conversation_state
    text = user_message.lower()

    # If last prompt was confirmation, handle yes/no
    if conversation_state.last_prompt == "confirm":
        if "yes" in text or "correct" in text:
            conversation_state.confirmed = True
        elif "no" in text:
            conversation_state = ConversationState()
            return "Okay, let's start over. What would you like to do?"
        else:
            return "Please reply 'yes' to confirm or 'no' to start over."

        # After confirmation, do the action
        start_time = conversation_state.date.replace(hour=conversation_state.hour, minute=conversation_state.minute, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        if conversation_state.intent == "check":
            free = is_time_slot_free(start_time, end_time)
            conversation_state = ConversationState()
            if free:
                return f"Yes, the slot on {start_time.strftime('%A, %B %d at %I:%M %p')} is available."
            else:
                return f"Sorry, that slot is already booked. Would you like to try another time?"
        elif conversation_state.intent == "book":
            free = is_time_slot_free(start_time, end_time)
            if not free:
                conversation_state = ConversationState()
                return f"Sorry, that slot is already booked. Would you like to try another time?"
            event = book_event(
                summary="Appointment via Tialor Talk",
                start_time=start_time,
                end_time=end_time,
                description="Booked through conversational agent."
            )
            conversation_state = ConversationState()
            if event:
                return f"Your appointment is booked for {start_time.strftime('%A, %B %d at %I:%M %p')}!"
            else:
                return "There was an error booking your appointment. Please try again."
        else:
            conversation_state = ConversationState()
            return "I'm not sure what you want to do. Please specify if you want to check or book a slot."

    # Figure out what the user wants to do
    if not conversation_state.intent:
        conversation_state.intent = parse_intent(text)
        if not conversation_state.intent:
            # If not a calendar intent, answer as a general question
            return answer_general_question(user_message)

    # Get the date
    if not conversation_state.date:
        date = parse_date(text)
        if date:
            conversation_state.date = date
        else:
            conversation_state.last_prompt = "date"
            return "For which date would you like to book or check availability?"

    # Get the time
    if conversation_state.hour is None or conversation_state.minute is None:
        hour, minute = parse_time(text)
        if hour is not None:
            conversation_state.hour = hour
            conversation_state.minute = minute
        else:
            conversation_state.last_prompt = "time"
            return "What time are you interested in? (e.g., 3pm, 14:00, afternoon)"

    # Confirm before booking/checking
    if not conversation_state.confirmed:
        dt_str = conversation_state.date.replace(hour=conversation_state.hour, minute=conversation_state.minute).strftime('%A, %B %d at %I:%M %p')
        conversation_state.last_prompt = "confirm"
        return f"Just to confirm, you want to {conversation_state.intent} a slot on {dt_str}? (yes/no)" 