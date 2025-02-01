# This python script is here to "act" as the ESP module and as PoC, so that I don't need to run an actual microcontroller to demonstrate
import random
import requests
import time

url = "http://localhost:8000/"

while True:
    temp_harri = round(random.uniform(10, 50), 1)
    temp_esp8266 = round(random.uniform(10, 50), 1)
    
    data_harri = {"temp": temp_harri, "source": "harri"}  # Use lowercase 'source'
    data_esp8266 = {"temp": temp_esp8266, "source": "esp8266"}  # Use lowercase 'source'
    
    try:
        x_harri = requests.post(url, data=data_harri)
        print(f"Harri: {x_harri}")
        
        x_esp8266 = requests.post(url, data=data_esp8266)
        print(f"ESP8266: {x_esp8266}")

    except Exception as e:
        print(e)
    
    time.sleep(5)