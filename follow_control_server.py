#!/usr/bin/python3
COMMAND_SERVER = input("Enter the command server URL (without trailing slash): ")

import ev3dev2.motor
print("Imported ev3dev2.motor")

steering_drive = ev3dev2.motor.MoveSteering(ev3dev2.motor.OUTPUT_B, ev3dev2.motor.OUTPUT_A)
print("Created steering_drive")



from ev3dev2.sensor.lego import ColorSensor as ev3dev2.sensor.lego.ColorSensor
print("Imported ev3dev2.sensor.lego")

import ev3dev2.sensor
print("Imported ev3dev2.sensor")

sensor_1 = ev3dev2.sensor.lego.ColorSensor(address=ev3dev2.sensor.INPUT_1)
print("Created sensor_1")

sensor_2 = ev3dev2.sensor.lego.ColorSensor(address=ev3dev2.sensor.INPUT_2)
print("Created sensor_2")

# import requests
# print("Imported requests")
import urllib.request
print("Imported urllib.request")
import urllib.parse
print("Imported urllib.parse")
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
        data = urllib.parse.urlencode({
                "sensor_1": sensor_1.raw,
                "sensor_2": sensor_2.raw,
            }).encode()
        req = urllib.request.Request(
            COMMAND_SERVER+"/commands",
            data=data
        )
        resp = urllib.request.urlopen(req,timeout=10)

        command = json.loads(resp.read().decode())

        steering_drive.on(command.get('steering',0), command.get('speed',0))
    except Exception as e:
        print(e)
        steering_drive.on(0,0)
        time.sleep(5)
    e = time.time()
    times.append((e-s))
    print("Command took:", (e-s) * 1000, "ms", "Average:", statistics.mean(times[-100:])*1000, "ms")