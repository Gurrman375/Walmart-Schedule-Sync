from playwright.sync_api import sync_playwright
from time import sleep

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(600000)
    page.goto("https://one.walmart.com/content/usone/en_us/me/my-schedule.html")
    sleep(1)

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
        print(f"Found response: {res.url} - {res.status}")
        print("Response Text:")
        print(res.text())
        print()  # For better readability between responses

    browser.close()