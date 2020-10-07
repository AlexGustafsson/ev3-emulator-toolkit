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
simulator: Simulator


@server.on("simulation_start")
def event_start(client_id, config):
    for port, type in config["motors"].items():
        simulator.brick.motors[port] = Motor(type)
    for port, type in config["sensors"].items():
        simulator.brick.sensors[port] = Sensor(type)
    simulator.start()


@server.on("simulation_step")
def event_step(client_id, count = 1):
    for i in range(count):
        simulator.step()
    server.emit("simulation_status_update", simulator.brick.to_dict())


@server.on("simulation_trigger_event")
def event_trigger_event(client_id, arguments: Dict[str, Any]):
    simulator.runtime.trigger_event(arguments["event"], **arguments["parameters"])


@server.event
def connect(session_id: str, environment):
    logging.info("Client connected session_id={}".format(session_id))


@server.event
def disconnect(session_id):
    logging.info("Client disconnected session_id={}".format(session_id))


def main(project_path: str) -> None:
    global simulator
    logging.basicConfig(level=logging.DEBUG)

    # Read the archive from the first parameter
    uf2 = UF2.read(project_path)
    project = Project(uf2)
    simulator = Simulator(project)

    app = WSGIApp(server)
    eventlet.wsgi.server(eventlet.listen(("", 3773)), app)


if __name__ == "__main__":
    main(sys.argv[1])
