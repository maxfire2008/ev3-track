import flask
import json
import inputs
import time

app = flask.Flask(__name__)

app.jinja_options["autoescape"] = lambda _: True

current_controller_state = {}

latest_data = {}

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
                print(event.code, event.state)
                current_controller_state[event.code] = event.state
        else:
            break
    # print("Controller state updated in:", time.time() - start)
    # return current_controller_state
    return {i: current_controller_state[i] for i in sorted(current_controller_state)}


def follow_controller(data=None):
    state = controller_state()
    return {
            "steering": int(
                (
                    100
                    if (state.get("ABS_X", 0)*(100/32768)) > 95 else
                    deadzone(state.get("ABS_X", 0))*(100/32768)
                )
                if state.get("BTN_WEST",0) else
                deadzone(state.get("ABS_X", 0))*((100/32768)/2)
            ),
            "speed": int(
                (
                    (9 if state.get("ABS_Z", 0)*(100/255) > 50 else 0)+1
                )
                *
                (
                    -((
                        state.get("ABS_RZ", 0)
                    )
                    *
                    (
                        (100/255)/10
                    ))
                    if state.get("BTN_SOUTH",0) else 
                    (
                        state.get("ABS_RZ", 0)
                    )
                    *
                    (
                        (100/255)/10
                    )
                )
            ),
        }

@app.route("/CONTROLLER_STATE", methods=["GET"])
def get_controller_state():
    return json.dumps(controller_state())


@app.route("/commands", methods=["POST"])
def get_commands():
    print(flask.request.data)
    for k in flask.request.json:
        latest_data[k] = flask.request.json[k]
    print(latest_data)
    return json.dumps(follow_controller(latest_data))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return flask.render_template('dashboard.html.j2', latest_data=latest_data, commands=follow_controller(latest_data))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
