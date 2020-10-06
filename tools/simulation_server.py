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
from tools.pxt.project import Project
from tools.uf2.uf2 import UF2


server = Server()
simulator: Simulator


# @server.event(namespace="/chat")
# def my_event(sid, data):
#     pass


@server.on("simulation_start")
def event_start(client_id):
    simulator.start()


@server.on("simulation_step")
def event_step(client_id, count = 1):
    # TODO: Callback here?
    for i in range(count):
        simulator.step()


@server.on("simulation_trigger_event")
def event_trigger_event(client_id, arguments: Dict[str, Any]):
    simulator.runtime.trigger_event(arguments["event"], **arguments["parameters"])


@server.event
def connect(session_id: str, environment):
    logging.info("Client connected session_id={}".format(session_id))
    # raise ConnectionRefusedError("authentication failed")
    # sio.emit("my event", {"data": "foobar"}, room=user_sid)
    # sio.emit("my event", {"data": "foobar"})


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
