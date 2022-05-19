COMMAND_SERVER = input("Enter the command server URL (without trailing slash): ")

import ev3dev2.motor
print("Imported ev3dev2.motor")

steering_drive = ev3dev2.motor.MoveSteering(ev3dev2.motor.OUTPUT_A, ev3dev2.motor.OUTPUT_B)
print("Created steering_drive")

import requests
print("Imported requests")
import time
print("Imported time")

while True:
    s = time.time()
    command = requests.get(COMMAND_SERVER+'/commands').json()
    steering_drive.on(command['steering'], command['speed'])
    e = time.time()
    print("Command took:", (e-s) * 1000, "ms")