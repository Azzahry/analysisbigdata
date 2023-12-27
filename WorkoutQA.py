import google.generativeai as palm
import streamlit as st
import datetime
import webbrowser
import re
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

palm.configure(api_key="AIzaSyAlptuKGaJcuANXUZD6xUR_-RujrA9Z2YY")
# credentials = service_account.Credentials.from_service_account_file(
#     'analysisbigdata-10655149f84f.json',  # Ganti dengan path ke file JSON kredensial Anda
#     scopes=['https://www.googleapis.com/auth/calendar']
# )
SCOPES=['https://www.googleapis.com/auth/calendar']

def cred():
    creds=None

    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json")
    
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES) # Ganti dengan path ke file JSON kredensial Anda
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())

    calendar_service = build('calendar', 'v3', credentials=creds)
    return calendar_service

def initiate(user_input, model):
  return palm.chat(messages=user_input)

def reply(self, user_input):
  return self.reply(user_input)

def extract_schedule(response_text):
    # Mencari hari-hari dalam teks menggunakan ekspresi reguler
    days_matches = re.findall(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', response_text)

    # Menghilangkan hari yang duplikat
    unique_days = list(set(days_matches))

    # Mengambil langkah-langkah untuk setiap hari
    schedule = {day: [] for day in unique_days}
    for day in unique_days:
        # Mencari langkah-langkah untuk setiap hari
        pattern = re.compile(rf"{day}:(.*?)(?:\n|$)")
        matches = pattern.findall(response_text)
        for match in matches:
            schedule[day].append(match.strip())

    return schedule

def add_event_to_calendar(day, summary, start_time, end_time):
    # Mengubah nama hari menjadi format yang sesuai dengan Google Calendar
    day_to_google_calendar = {
        'Monday': 'MO',
        'Tuesday': 'TU',
        'Wednesday': 'WE',
        'Thursday': 'TH',
        'Friday': 'FR',
        'Saturday': 'SA',
        'Sunday': 'SU'
    }

    if day in day_to_google_calendar:
      recurrence_rule = f"RRULE:FREQ=WEEKLY;BYDAY={day_to_google_calendar[day]};COUNT=1"
      event = {
          'summary': summary,
          'start': {
              'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
              'timeZone': 'Asia/Jakarta',
          },
          'end': {
              'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
              'timeZone': 'Asia/Jakarta',
          },
          'recurrence': [recurrence_rule]
      }
    event = calendar_service.events().insert(calendarId='primary', body=event).execute()
    print(f'Acara ditambahkan: {event.get("htmlLink")}')
    return event['id']

models = [m for m in palm.list_models() if 'generateMessage' in m.supported_generation_methods]
model = models[0].name
print(model)


st.title("Workout QA")
prompt = st.text_input("Enter a message:")

if st.button('Generate'):
  response = initiate(
      user_input=prompt,
      model=model,
  )
  st.write(response.last)
  schedule = extract_schedule(response.last)

  calendar_service = cred()

  for day, steps in schedule.items():
      for i, step in enumerate(steps):
          start_time = datetime.datetime.now() + datetime.timedelta(days=i)
          end_time = start_time + datetime.timedelta(minutes=15)  # Asumsikan setiap langkah berlangsung selama satu jam
          event_id = add_event_to_calendar(day=day, summary=step, start_time=start_time, end_time=end_time)
          st.write(f"Step {i+1}: {step} on {day} (Event ID: {event_id})")

if st.button("Go to Google Calendar"):
    webbrowser.open("https://calendar.google.com")