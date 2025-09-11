import  json
import os.path, sys
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
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

    current_time = datetime.now(timezone.utc).astimezone()

    offset_str = current_time.strftime('%z')

    current_timezone = f"{offset_str[0:3]}:{offset_str[3:]}"
    try:
        os.system("playwright install")
    except Exception as e:
        print(e)
        waitTill()
        sys.exit(-1)
        
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(600000)
            page.goto("https://one.walmart.com/content/usone/en_us/me/my-schedule.html")
            sleep(30)

            # Collect all responses
            responses = []
            def handle_response(res):
                responses.append(res)

            page.on("response", handle_response)

            # Wait for the specific request to be made
            page.wait_for_url("https://one.walmart.com/content/usone/en_us/me/my-schedule.html")

            # Filter responses by URL pattern
            target_url = "https://one.walmart.com/bin/adp/onprem/snapshot.api"
            filtered_responses = [res for res in responses if res.url.startswith(target_url)]

            # Print filtered responses and response text
            for res in filtered_responses:
                # print(f"Found response: {res.url} - {res.status}")
                # print("Response Text:")
                if(res.text()):
                    response = res.text()
                    break

            browser.close()
    except Exception as e:
        print(e)
        waitTill()

    response = json.loads(response)

    creds = None

    if os.path.exists("tokens.json"):
        creds = Credentials.from_authorized_user_file("tokens.json")
        print("Token Path Exists")
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
        print("Wrote Token")

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
            # print("Week:", a["wmWeek"])
            for b in a["schedules"]:
                for c in b["events"]:
                    if(c["type"] == "Job"):
                        event = {
                            "summary": c["jobDescription"],
                            "description": "Your job",
                            "start": {
                                "dateTime": c["startTime"]+":00"+current_timezone, #-11:00 to +14:00
                            },
                            "end": {
                                "dateTime": c["endTime"]+":00"+current_timezone,
                            },
                            "reminders": {
                                "useDefault": False,
                                "overrides": [
                                    {
                                        "method": "popup",
                                        "minutes": 60
                                    }
                                ]
                            }
                        }
                        event = service.events().insert(calendarId=calendar, body=event).execute()
                        # print(f"Event created {event.get('htmlLink')}")
                    elif(c["type"] == "Meal"):
                        print()
                        # print(f"Meal Start: {c['startTime']}, Meal End: {c['endTime']}")
        
        now = dt.datetime.now(tz=dt.timezone.utc).astimezone().isoformat()
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
        # print(f"Event created {event.get('htmlLink')}")
        waitTill()
    except HttpError as error:
        print("An error occured:", error)
        waitTill()

if __name__ == "__main__":
    main()