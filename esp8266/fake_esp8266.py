#This python script is here to "act" as the ESP module and as PoC, so that I don't need to run an actual microcontroller to demonstrate
import random
import requests
import time


url = "http://localhost:8000/"

while(True):
    temp=round(random.uniform(10,50),1)
    data = {"temp":temp}
    try:
        x = requests.post(url, data = data)
        print(x)

    except Exception as e:
        print(e)
    time.sleep(5)