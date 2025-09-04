import requests, json
import os.path
import time
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

    time.sleep(5)

    print("Timezone that is appropriate to you from -11:00 to +14:00. Include + or Minus. Do not include labels like PST, EST, MST, or other.")
    timezone = input("Enter a timezone (-11:00 to +14:00): ")

    print("Enter store number. Currently only works with store numbers.")
    store_number = input("Store Number: ")

    print("The WIN can be found on the app under profile")
    win = input("WIN: ")

    print("To get the nessesary cookie login in to One Walmart using this link: https://one.walmart.com/content/usone/en_us/me/my-schedule.html")

    print("From there run the command Control + I to pull up dev tools. Then look under network and in the filter bar copy and paste: https://one.walmart.com/bin/adp/onprem/snapshot.api=schedule.win")

    print("The cookie is under request headers. Copy the cookie")

    cookie = input("Enter the cookie found from https://one.walmart.com/content/usone/en_us/me/my-schedule.html:")


    headers = {
        'Cookie': f'{cookie}',
    }

    response = requests.get(
        f'https://one.walmart.com/bin/adp/onprem/snapshot.api=schedule.win={win}.store={store_number}.json',
        headers=headers,
        #cookies=cookies,
    )
    response = json.loads(response.text)

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")
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

        service = build("calendar", "v3", credentials=creds)
        calendar_list = service.calendarList().list().execute()
        for calendar in calendar_list['items']:
          if(calendar['summary'] == "Walmart"):
              calendar = calendar["id"]

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
