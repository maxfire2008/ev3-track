import ev3dev2.motor
import json

COMMAND_SERVER = input("Enter the command server URL (without trailing slash): ")

steering_drive = ev3dev2.motor.MoveSteering(ev3dev2.motor.OUTPUT_A, ev3dev2.motor.OUTPUT_B)

while True:
    command = requests.get(COMMAND_SERVER+'/commands').json()
    steering_drive.on(command['steering'], command['speed'])