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

conn.modules["ev3dev2.sensor.lego"]
conn.modules["ev3dev2.sensor"]
sensor_colour_left = conn.modules.ev3dev2.sensor.lego.ColorSensor(conn.modules.ev3dev2.sensor.INPUT_1)
sensor_colour_right = conn.modules.ev3dev2.sensor.lego.ColorSensor(conn.modules.ev3dev2.sensor.INPUT_4)

class ControllerEvent:
    def __init__(self, code, state):
        self.code = code
        self.state = state


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

LATEST_SENSORS = {
    "colour_left": (0, 0, 0),
    "colour_right": (0, 0, 0),
    "ultrasonic": 0,
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


def geo_fence(mouse_position, pos_x, pos_y, len_x, len_y):
    if mouse_position[0] > pos_x and mouse_position[0] < pos_x + len_x and mouse_position[1] > pos_y and mouse_position[1] < pos_y + len_y:
        return True
    return False


LAST_UPDATE = 0
MOUSEDOWNON = None

while True:
    events = []
    try:
        events_read = inputs.devices.gamepads[0].read()
        while events_read:
            events += events_read
            events_read = inputs.devices.gamepads[0].read()
    except IndexError:
        pass
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     mouse_position = pygame.mouse.get_pos()
        #     if geo_fence(mouse_position, 1160, 10, 100, 600):
        #         MOUSEDOWNON = "speed"
        # elif event.type == pygame.MOUSEBUTTONUP:
        #     if MOUSEDOWNON == "speed":
        #         events.append(ControllerEvent("ABS_RZ", 0))
        #     MOUSEDOWNON = None
        # if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION) and MOUSEDOWNON == "speed":
        #     mouse_position = pygame.mouse.get_pos()
        #     events.append(ControllerEvent("ABS_RZ", int(
        #         limit(
        #             snapzone(
        #                 deadzone(
        #                     255-((mouse_position[1]-10)/(300/255)),
        #                     deadzone=int(0.1*255),
        #                 ),
        #                 snapzone=int(0.95*255),
        #                 snapto=255
        #             ),
        #             -255,
        #             255
        #         )
        #     )))
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

    LATEST_SENSORS["colour_left"] = sensor_colour_left.raw
    LATEST_SENSORS["colour_right"] = sensor_colour_right.raw

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

    # draw circle for colour_left
    pygame.draw.circle(
        screen,
        [max(i, 255) for i in LATEST_SENSORS["colour_left"]],
        (1160, 300),
        10,
        0
    )
    # draw circle for colour_right
    pygame.draw.circle(
        screen,
        [max(i/1020, 255) for i in LATEST_SENSORS["colour_right"]],
        (1160, 500),
        10,
        0
    )

    pygame.display.flip()
