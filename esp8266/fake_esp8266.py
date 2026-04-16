# This python script is here to "act" as the ESP module and as PoC, so that I don't need to run an actual microcontroller to demonstrate
import random
import requests
import time
import hmac
import hashlib
import os

API_SECRET = os.getenv("API_SECRET")
url = "http://localhost:8000/api/"

def make_request(temp, humidity, source):
    timestamp = str(int(time.time()))

    message = f"{temp}:{humidity}:{source}:{timestamp}"
    signature = hmac.new(
        API_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return {
        "temp": temp,
        "humidity": humidity,
        "source": source,
        "timestamp": timestamp,
        "hash": signature
    }

while True:
    try:
        for source in ["harri", "esp8266"]:
            temp = round(random.uniform(10, 50), 1)
            humidity = round(random.uniform(20, 80), 1)
            payload = make_request(temp, humidity, source)
            r = requests.post(url, data=payload)

            print(source, r.status_code, r.text)

    except Exception as e:
        print(e)

    time.sleep(5)