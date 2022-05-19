import flask
import json
import inputs
import time

app = flask.Flask(__name__)

current_controller_state = {}

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)