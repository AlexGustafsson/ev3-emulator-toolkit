import sys
import logging
import json
from threading import Thread
from queue import Queue
from typing import Dict, Union, Any
from base64 import b64decode

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

log = logging.getLogger(__name__)
server = Server()
simulators: Dict[str, Simulator] = {}

@server.on("simulation_create")
def event_create(client_id: str, data: bytes) -> None:
    try:
        uf2 = UF2.parse(data)
        project = Project(uf2)
        simulator = Simulator(project)
        simulators[client_id] = simulator
        return True
    except Exception:
        log.error("Unable to create simulation", exc_info=True)
        return False


@server.on("simulation_start")
def event_start(client_id: str, config):
    for port, type in config["motors"].items():
        simulators[client_id].brick.motors[port] = Motor(type)
    for port, type in config["sensors"].items():
        simulators[client_id].brick.sensors[port] = Sensor(type)
    simulators[client_id].start()


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
    log.info("Client connected client_id={}".format(client_id))


@server.event
def disconnect(client_id: str):
    log.info("Client disconnected client_id={}".format(client_id))
    del simulators[client_id]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] [%(module)s] %(message)s')

    app = WSGIApp(server)
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 3773)), app)


if __name__ == "__main__":
    main()
