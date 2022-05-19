import flask
import json
import inputs
import time

app = flask.Flask(__name__)

current_controller_state = {}

def deadzone(value, deadzone=4096):
    if value < deadzone and value > -deadzone:
        return 0
    else:
        return value

def controller_state():
    start = time.time()
    global current_controller_state
    while True:
        events = inputs.devices.gamepads[0].read()
        # print(events)
        if events:
            for event in events:
                print(event.code,event.state)
                current_controller_state[event.code] = event.state
        else:
            break
    print("Controller state updated in:", time.time() - start)
    # return current_controller_state
    return {i:current_controller_state[i] for i in sorted(current_controller_state)}

@app.route("/CONTROLLER_STATE", methods=["GET"])
def get_controller_state():
    return json.dumps(controller_state())

@app.route("/commands", methods=["GET"])
def get_commands():
    state = controller_state()
    return json.dumps(
        {
            "steering": int(deadzone(state.get("ABS_X",0))*0.011138916),
            "speed": int(state.get("ABS_RZ",0)*0.392156863),
        }
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)