import sys
import logging
import json
from threading import Thread
from queue import Queue
from typing import Dict, Union, Any

# Requires Eventlet
# python3 -m pip install eventlet
import eventlet
# Requires Socket IO
# python3 -m pip install python-socketio
from socketio import Server, WSGIApp

from tools.ev3.simulation.simulator import Simulator
from tools.ev3.simulation.brick import Motor, Sensor
from tools.pxt.project import Project
from tools.uf2.uf2 import UF2


server = Server()
project: Project

simulators: Dict[str, Simulator] = {}

@server.on("simulation_start")
def event_start(client_id: str, config):
    simulator = Simulator(project)
    for port, type in config["motors"].items():
        simulator.brick.motors[port] = Motor(type)
    for port, type in config["sensors"].items():
        simulator.brick.sensors[port] = Sensor(type)
    simulators[client_id] = simulator
    simulator.start()


@server.on("simulation_step")
def event_step(client_id: str, count = 1):
    for i in range(count):
        simulators[client_id].step()
    return simulators[client_id].brick.to_dict()


@server.on("simulation_trigger_event")
def event_trigger_event(client_id: str, arguments: Dict[str, Any]):
    simulators[client_id].runtime.trigger_event(arguments["event"], **arguments["parameters"])


@server.event
def connect(client_id: str, environment):
    logging.info("Client connected client_id={}".format(client_id))


@server.event
def disconnect(client_id: str):
    logging.info("Client disconnected client_id={}".format(client_id))
    del simulators[client_id]


def main(project_path: str) -> None:
    global project

    logging.basicConfig(level=logging.DEBUG)

    # Read the archive from the first parameter
    uf2 = UF2.read(project_path)
    project = Project(uf2)

    app = WSGIApp(server)
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 3773)), app)


if __name__ == "__main__":
    main(sys.argv[1])
