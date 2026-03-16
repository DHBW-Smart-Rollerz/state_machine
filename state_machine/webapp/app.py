import asyncio
import json
import os
import sys
import threading
import time
from threading import Thread

import websockets
from flask import Flask, Response, jsonify, render_template

from state_machine.components.state_description import BlackBoard


# Disable printing to stdout
class NullWriter:
    """
    A utility class that temporarily suppresses all output to the standard output (stdout).

    This class redirects `sys.stdout` to itself, effectively silencing any print statements
    or other output to the console. When the instance is deleted, the original `sys.stdout`
    is restored.

    Methods:
        write(_): A no-op method that discards any input.
        flush(): A no-op method to comply with the file-like interface.

    Attributes:
        original_stdout: Stores the original `sys.stdout` to restore it later.
    """

    def write(self, _):
        """Suppresses output by doing nothing."""
        pass

    def flush(self):
        """Suppresses output by doing nothing."""
        pass

    def __init__(self):
        """Initialize the NullWriter and redirect stdout."""
        self.original_stdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        """Restore the original stdout when the NullWriter is deleted."""
        sys.stdout = self.original_stdout


def create_app(blackboard: BlackBoard):
    """
    Create and configure a Flask web application.

    This function initializes a Flask application and sets up routes for
    interacting with a blackboard object, which contains various parameters
    and data related to the application's state. The application provides
    endpoints to retrieve parameters, render an index page, and stream
    real-time updates.

    Args:
        blackboard (BlackBoard): An object containing the application's state
        and data, such as light configuration, speed, lane information,
        objects, and signs.

    Returns:
        Flask: A configured Flask application instance.

    Routes:
        /parameters (GET):
            Returns:
                JSON: A JSON representation of the blackboard parameters,
                including light configuration, speed, lane information,
                objects, and signs.

        / (GET):
            Returns:
                HTML: Renders the index.html template.

        /stream (GET):
            Returns:
                Event Stream: A server-sent event (SSE) stream that provides
                real-time updates of the blackboard parameters in JSON format.

    Notes:
        - The `get_blackboard_params` function is used internally to extract
          and format the blackboard data for the web interface.
        - The `/stream` route streams updates every 0.1 seconds.
    """
    app = Flask(__name__)
    app.blackboard = blackboard

    def get_blackboard_params():
        """
        Retrieve and format blackboard parameters for the web interface.

        This function extracts relevant data from the `app.blackboard` object and
        organizes it into a dictionary format suitable for use in the web application.
        It includes information about the light configuration, maximum speed, goal lane,
        car lane, objects, and signs.

        Returns:
            dict: A dictionary containing the following keys:
                - "light_configuration" (str): The light configuration as a string.
                - "max_speed" (varied): The maximum speed value from the blackboard.
                - "goal_lane" (str): The goal lane as a string.
                - "car_lane" (str): The car's current lane as a string.
                - "objects" (list): A list of dictionaries representing objects,
                  each containing:
                    - "id" (varied): The object's ID.
                    - "name" (str): The object's name as a string.
                    - "location" (str): The object's location as a string.
                    - "distance" (varied): The object's distance.
                - "signs" (list): A list of dictionaries representing signs,
                  each containing:
                    - "id" (varied): The sign's ID.
                    - "name" (str): The sign's name as a string.
                    - "location" (str): The sign's location as a string.
                    - "distance" (varied): The sign's distance.
        """
        params = {
            "current_state": str(app.blackboard.current_state),
            "light_configuration": str(app.blackboard.light_configuration),
            "max_speed": app.blackboard.max_speed,
            "goal_lane": str(app.blackboard.goal_lane),
            "car_lane": str(app.blackboard.car_lane),
            "speed_limit": str(app.blackboard.speed_limit),
            "objects": [],
            "signs": [],
            "lane_coefficients": {},
        }

        # Add lane coefficients data
        for side, poly in app.blackboard.lane_coefficients.items():
            # poly1d stores coefficients high-to-low; reverse back to low-to-high
            # for readability: [a, b, c, ...] → a + b*x + c*x² + ...
            params["lane_coefficients"][side] = [
                round(float(c), 4) for c in reversed(poly.coeffs)
            ]

        # Add objects data
        if hasattr(app.blackboard, "objects") and app.blackboard.objects:
            params["objects"] = [
                {
                    "id": obj["id"],
                    "name": str(obj["name"]),
                    "location": str(obj["location"]),
                    "distance": round(float(obj["distance"]), 1),
                    "x": round(float(obj["position"]["x"]), 1),
                    "y": round(float(obj["position"]["y"]), 1),
                    "width": round(float(obj.get("width", 200)), 1),
                    "debug": obj.get("debug", {}),
                }
                for obj in app.blackboard.objects
            ]

        # Add signs data
        if hasattr(app.blackboard, "signs") and app.blackboard.signs:
            params["signs"] = [
                {
                    "id": sign["id"],
                    "name": str(sign["name"]),
                    "location": str(sign["location"]),
                    "distance": round(float(sign["distance"]), 1),
                    "x": round(float(sign["position"]["x"]), 1),
                    "y": round(float(sign["position"]["y"]), 1),
                    "debug": sign.get("debug", {}),
                }
                for sign in app.blackboard.signs
            ]

        return params

    @app.route("/parameters", methods=["GET"])
    def parameters():
        """
        Retrieves and returns the blackboard parameters as a JSON response.

        Returns:
            flask.Response: A JSON response containing the blackboard parameters.
        """
        return jsonify(get_blackboard_params())

    @app.route("/", methods=["GET"])
    def index():
        """
        Renders the index page of the web application.

        Returns:
            Response: The rendered HTML template for the index page.
        """
        return render_template("index.html")

    @app.route("/stream", methods=["GET"])
    def stream():
        """
        Stream data to the client using Server-Sent Events (SSE).

        This function sets up a streaming response that continuously sends
        JSON-encoded data to the client. The data is fetched from a blackboard
        (shared state) and sent at regular intervals.

        Returns:
            Response: A Flask Response object with the "text/event-stream" MIME type,
            which streams data to the client in real-time.
        """
        pass

        def generate():
            """Generates the data stream."""
            while True:
                params = get_blackboard_params()
                yield f"data: {json.dumps(params)}\n\n"
                time.sleep(0.1)

        return Response(generate(), mimetype="text/event-stream")

    return app


async def websocket_handler(websocket, _, blackboard):
    """
    Handles WebSocket communication by continuously sending the current state of the blackboard to the connected WebSocket client.

    Args:
        websocket (WebSocket): The WebSocket connection to the client.
        _ (Any): Placeholder for an unused argument.
        blackboard (object): An object containing the state information to be sent to the client.

    Behavior:
        - Constructs a dictionary of parameters from the blackboard's attributes.
        - Sends the parameters as a JSON-encoded string to the WebSocket client.
        - Repeats the process every 0.1 seconds indefinitely.
    """
    while True:
        lane_coefs = {}
        for side, poly in blackboard.lane_coefficients.items():
            lane_coefs[side] = [round(float(c), 4) for c in reversed(poly.coeffs)]

        params = {
            "current_state": str(blackboard.current_state),
            "light_configuration": str(blackboard.light_configuration),
            "max_speed": blackboard.max_speed,
            "goal_lane": str(blackboard.goal_lane),
            "car_lane": str(blackboard.car_lane),
            "speed_limit": str(blackboard.speed_limit),
            "lane_coefficients": lane_coefs,
            "objects": [
                {
                    "id": obj["id"],
                    "name": str(obj["name"]),
                    "location": str(obj["location"]),
                    "distance": round(float(obj["distance"]), 1),
                    "x": round(float(obj["position"]["x"]), 1),
                    "y": round(float(obj["position"]["y"]), 1),
                    "width": round(float(obj.get("width", 200)), 1),
                    "debug": obj.get("debug", {}),
                }
                for obj in (blackboard.objects or [])
            ],
            "signs": [
                {
                    "id": sign["id"],
                    "name": str(sign["name"]),
                    "location": str(sign["location"]),
                    "distance": round(float(sign["distance"]), 1),
                    "x": round(float(sign["position"]["x"]), 1),
                    "y": round(float(sign["position"]["y"]), 1),
                    "debug": sign.get("debug", {}),
                }
                for sign in (blackboard.signs or [])
            ],
        }
        await websocket.send(json.dumps(params))
        await asyncio.sleep(0.1)


def create_and_run_flask_app(blackboard):
    """
    Creates and runs a Flask application alongside a WebSocket server.

    This function initializes a Flask application using the provided blackboard object
    and starts it in a separate thread. Additionally, it sets up and runs a WebSocket
    server asynchronously on a different port.

    Args:
        blackboard: An object used to share data between the Flask application and the WebSocket server.

    The Flask application runs on host "0.0.0.0" and port 5001 with debugging and reloading disabled.
    The WebSocket server listens on host "0.0.0.0" and port 6789.
    """
    app = create_app(blackboard)

    def run_flask():
        app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

    async def run_websocket():
        server = await websockets.serve(
            lambda ws: websocket_handler(ws, "/", blackboard),
            "0.0.0.0",
            6789,
        )
        await server.wait_closed()

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_websocket())
