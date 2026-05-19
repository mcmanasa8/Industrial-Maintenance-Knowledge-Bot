import requests
import os

from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

def send_alert(message):

    data = {
        "message": message
    }

    response = requests.post(
        WEBHOOK_URL,
        json=data
    )

    return response.status_code