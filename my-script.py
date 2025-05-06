#!/usr/bin/python3

import time
import requests


API_URL = "https://duck-active-buffalo.ngrok-free.app/ping-api"
URL = "https://hooks.slack.com/services/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"

def send_message_to_slack(url, message):
    """
    Send a message to Slack using a specified URL.

    Args:
        url (str): The Slack webhook URL for sending messages.
        message (dict): The JSON-formatted message to be sent to Slack.

    Raises:
        Exception: If the response status code is not 200

    Returns:
        None
    """
    response = requests.post(url, json=message)

    if response.status_code != 200:
        print("SLLACKK integration on shared systeem is not working")

def ping_api(url):
    try:
        # Sending a GET request to the API
        response = requests.get(url)

        # Checking if the API responded successfully
        if response.status_code == 200:
            print(f"Shared System API is reachable. Status Code: {response.status_code}")

        else:
            message = {"text": "<!channel> The Windows server on the shared system is not running. Please check it as soon as possible."}
            send_message_to_slack(URL, message)

    except requests.exceptions.RequestException as e:
        print(f"Failed to reach the API. Error: {e}")

# Replace this URL with the actual API endpoint you want to ping

def main():
    while True:
        # time.sleep(120)
        ping_api(API_URL)
        time.sleep(600)


if __name__ == "__main__":
    main()
