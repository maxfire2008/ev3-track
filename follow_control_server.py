#!/usr/bin/python3
COMMAND_SERVER = input("Enter the command server URL (without trailing slash): ")

import ev3dev2.motor
print("Imported ev3dev2.motor")

steering_drive = ev3dev2.motor.MoveSteering(ev3dev2.motor.OUTPUT_A, ev3dev2.motor.OUTPUT_B)
print("Created steering_drive")

# import requests
# print("Imported requests")
import urllib.request
print("Imported urllib.request")
import time
print("Imported time")
import statistics
print("Imported statistics")
import json
print("Imported json")

times = []
while True:
    s = time.time()
    try:
        # command = requests.get(COMMAND_SERVER+"/commands").json()
        req = urllib.request.urlopen(COMMAND_SERVER+"/commands", timeout=30)
        command = json.loads(req.read().decode())

        steering_drive.on(command['steering'], command['speed'])
    except Exception as e:
        print(e)
        steering_drive.on(0,0)
        time.sleep(5)
    e = time.time()
    times.append((e-s))
    print("Command took:", (e-s) * 1000, "ms", "Average:", statistics.mean(times[-100:])*1000, "ms")