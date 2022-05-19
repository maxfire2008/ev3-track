import flask
import json
import inputs

app = flask.Flask(__name__)

current_controller_state = {}
def controller_state():
    global current_controller_state
    for event in inputs.devices.gamepads[0].read():
        current_controller_state[event.code] = event.state
    return current_controller_state

@app.route("/CONTROLLER_STATE", methods=["GET"])
def get_controller_state():
    return json.dumps(controller_state())

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)