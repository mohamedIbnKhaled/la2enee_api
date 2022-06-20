import os
from dotenv import load_dotenv
import requests
import json
load_dotenv()
def createBody(deviceToken,massage,title):
    body = {
        "notification": {"title": title, "body":massage ,
        "click_action": "FLUTTER_NOTIFICATION_CLICK", },
        "to": deviceToken,
        "priority": "high",
        "screen": "screenA",
    }
    return body

def massaging(body):
    serverToken = os.environ['serverToken']
    headers = {
        "Content-Type": "application/json",
        "Authorization": "key=" + serverToken,
        }
    response = requests.post(
        "https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body)
    )
    return response.status_code