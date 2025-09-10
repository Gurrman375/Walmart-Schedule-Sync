# This is used to test calendar inputs

import requests, json
import os.path
from time import sleep
import datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def waitTill():
    input("Press any key to continue ...")

def main():
    print("*"*32)
    print("Walmart Schedule Sync")
    print("*"*32)

    sleep(5)

    print("Timezone that is appropriate to you from -11:00 to +14:00. Include + or Minus. Do not include labels like PST, EST, MST, or other.")
    timezone = input("Enter a timezone (-11:00 to +14:00): ")


    response = {} # Test Response to calendar
    creds = 0

    if os.path.exists("tokens.json"):
        creds = Credentials.from_authorized_user_file("tokens.json")
        print("Testing Tokens")
    elif not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Tokens")
            creds.refresh(Request())
        else:
            print("Starting server")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
    
    with open("tokens.json", "w") as token:
        token.write(creds.to_json())
        print("wrote token")

    try:
        service = build("calendar", "v3", credentials=creds)
        calendar_list = service.calendarList().list().execute()
        for calendar in calendar_list['items']:
            if(calendar['summary'] == "Walmart"):
                calendar = calendar["id"]
                print(f"Found Walmart Calendar: {calendar}")
                break
            else:
                print("Looking for Calendar")        

        for a in response["payload"]["weeks"]:
            print("Week:", a["wmWeek"])
            for b in a["schedules"]:
                for c in b["events"]:
                    if(c["type"] == "Job"):
                        event = {
                            "summary": c["jobDescription"],
                            "description": "Your job",
                            "start": {
                                "dateTime": c["startTime"]+":00"+timezone, #-11:00 to +14:00
                            },
                            "end": {
                                "dateTime": c["endTime"]+":00"+timezone,
                            }
                        }
                        event = service.events().insert(calendarId=calendar, body=event).execute()
                        print(f"Event created {event.get('htmlLink')}")
                    elif(c["type"] == "Meal"):
                        print(f"Meal Start: {c['startTime']}, Meal End: {c['endTime']}")
        
        now = dt.datetime.now(tz=dt.timezone.utc).isoformat()
        three_weeks_from_now = dt.datetime.fromisoformat(now) + dt.timedelta(days=14)
        three_weeks_from_now = three_weeks_from_now - dt.timedelta(days=three_weeks_from_now.weekday())
        event = {
            "summary": "Refresh Sync",
            "description": "Use Walmart Schedule Sync to refresh schedule on",
            "start": {
                "dateTime": three_weeks_from_now.isoformat(), #-11 to +14
            },
            "end": {
                "dateTime": three_weeks_from_now.isoformat(), #-11 to +14
            }
        }
        event = service.events().insert(calendarId=calendar, body=event).execute()
        print(f"Event created {event.get('htmlLink')}")
        waitTill()
    except HttpError as error:
        print("An error occured:", error)
        waitTill()

if __name__ == "__main__":
    main()