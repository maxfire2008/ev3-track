import rpyc
import inputs
import time
import pygame

conn = rpyc.classic.connect('192.168.137.3')

# pygame initilize with window of 1280x720
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Remote Control')

conn.modules["ev3dev2.motor"]
steering_drive = conn.modules.ev3dev2.motor.MoveSteering(
    conn.modules.ev3dev2.motor.OUTPUT_B, conn.modules.ev3dev2.motor.OUTPUT_A)


def deadzone(value, deadzone=4096):
    if value < deadzone and value > -deadzone:
        return 0
    else:
        return value


def snapzone(value, snapzone=95, snapto=100):
    if value > snapzone:
        return snapto
    elif value < -snapzone:
        return -snapto
    else:
        return value

COLOURS = {
    "background": (255, 255, 255),
    "text": (0, 0, 0),
    "speed_control_background": (200, 200, 200),
    "speed_control_filled": (255, 0, 0),
    "steering_control_background": (200, 200, 200),
    "steering_control_filled": (0, 0, 255),
}

OUTPUTS = {
    "steering": 0,
    "speed": 0,
    "speed_influence": 0,
    "steering_mode": 0,
}

OUTPUTS_PREVIOUS = OUTPUTS.copy()


def limit(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def wrap_around(value, min_value, max_value):
    return (value - min_value) % (max_value+1 - min_value) + min_value


def changed(keys):
    global OUTPUTS
    global OUTPUTS_PREVIOUS
    for key in keys:
        if OUTPUTS[key] != OUTPUTS_PREVIOUS[key]:
            return True
    return False


def toggle(value):
    if value == False:
        return True
    return False


def increase_above_below(value, increase, leavezero=True):
    if leavezero and value == 0:
        return value
    if value > 0:
        return value + increase
    else:
        return value - increase


def get_steering_mode(outputs):
    steering_modes = ["auto", "normal", "literal", "full"]
    outputs["steering_mode"] = wrap_around(
        outputs.get("steering_mode", 0),
        0,
        len(steering_modes)-1
    )
    return steering_modes[outputs.get("steering_mode", 0)]


def get_steering(outputs):
    if get_steering_mode(outputs) == "auto":
        commanded_steering = outputs.get("steering", 0)
        if commanded_steering < 50 and commanded_steering > -50:
            return int(outputs.get("steering", 0)/2)
        else:
            return int(
                increase_above_below(
                    outputs.get("steering", 0)/2,
                    50,
                    True
                )
            )
    elif get_steering_mode(outputs) == "normal":
        return int(outputs.get("steering", 0)/4)
    elif get_steering_mode(outputs) == "literal":
        return int(outputs.get("steering", 0))
    elif get_steering_mode(outputs) == "full":
        return int(
            increase_above_below(
                outputs.get("steering", 0)/2,
                50,
                True
            )
        )
    return 0


def get_speed_influence(outputs):
    possible_speeds = [0.1, 0.25, 0.5, 0.75, 1]
    outputs["speed_influence"] = limit(outputs.get(
        "speed_influence", 1), 0, len(possible_speeds)-1)
    return possible_speeds[outputs.get("speed_influence", 1)]


def get_speed(outputs):
    return int(
        outputs.get("speed", 0)*get_speed_influence(outputs)
    )


LAST_UPDATE = 0
while True:
    try:
        events = inputs.devices.gamepads[0].read()
    except IndexError:
        events = None
    if events:
        for event in events:
            print(event.code, event.state)
            if event.code == "ABS_X":
                OUTPUTS["steering"] = int(
                    deadzone(event.state)*(100/32768)
                )
            if event.code == "ABS_RZ":
                OUTPUTS["speed"] = int(
                    event.state
                    *
                    (
                        (100/255)
                    )
                )
            if event.code == "ABS_Z":
                OUTPUTS["speed"] = int(
                    -(
                        event.state
                        *
                        (
                            (100/255)
                        )
                    )
                )
            if event.code == "BTN_WEST":
                if event.state:
                    OUTPUTS["steering_mode"] += 1
            if event.code == "ABS_HAT0X" and event.state == 1:
                OUTPUTS["speed_influence"] += 1
            if event.code == "ABS_HAT0X" and event.state == -1:
                OUTPUTS["speed_influence"] -= 1
    # pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if time.time() - LAST_UPDATE > 0.05:
        if changed(["steering", "speed", "speed_influence", "steering_mode"]):
            steering_drive.on(
                steering=get_steering(OUTPUTS),
                speed=get_speed(OUTPUTS),
            )

        OUTPUTS_PREVIOUS = OUTPUTS.copy()
        LAST_UPDATE = time.time()
    # pygame screen update
    screen.fill(COLOURS["background"])
    # pygame draw text

    font = pygame.font.SysFont("monospace", 20)
    steering_text = font.render(
        "Steering: " + str(get_steering(OUTPUTS)),
        True,
        COLOURS["text"]
    )
    screen.blit(steering_text, (10, 10))

    speed_text = font.render(
        "Speed: " + str(get_speed(OUTPUTS)),
        True,
        COLOURS["text"]
    )
    screen.blit(speed_text, (10, 30))

    commanded_steering_text = font.render(
        "Commanded Steering: " + str(OUTPUTS.get("steering", 0)),
        True,
        COLOURS["text"]
    )
    screen.blit(commanded_steering_text, (10, 50))

    commanded_speed_text = font.render(
        "Commanded Speed: " + str(OUTPUTS.get("speed", 0)),
        True,
        COLOURS["text"]
    )
    screen.blit(commanded_speed_text, (10, 70))

    speed_influence_text = font.render(
        "Speed Influence: " + str(OUTPUTS.get("speed_influence", 1)) + " (" +
        str(get_speed_influence(OUTPUTS)) + ")",
        True,
        COLOURS["text"]
    )
    screen.blit(speed_influence_text, (10, 90))

    steering_mode = font.render(
        "Steering Mode: " + get_steering_mode(OUTPUTS),
        True,
        COLOURS["text"]
    )
    screen.blit(steering_mode, (10, 110))

    all_outputs_text = font.render(
        "All Outputs: " + str(OUTPUTS),
        True,
        COLOURS["text"]
    )
    screen.blit(all_outputs_text, (10, 700))

    pygame.draw.rect(
        screen,
        COLOURS["speed_control_background"],
        pygame.Rect(
            1160,
            10,
            100,
            600
        )
    )

    if OUTPUTS.get("speed", 0) > 0:
        pygame.draw.rect(
            screen,
            COLOURS["speed_control_filled"],
            pygame.Rect(
                1160,
                (300-OUTPUTS.get("speed", 0)*(300/100))+10,
                100,
                OUTPUTS.get("speed", 0)*(300/100)
            )
        )
    elif OUTPUTS.get("speed", 0) < 0:
        pygame.draw.rect(
            screen,
            COLOURS["speed_control_filled"],
            pygame.Rect(
                1160,
                310,
                100,
                (-OUTPUTS.get("speed", 0))*(300/100)
            )
        )

    pygame.display.flip()
