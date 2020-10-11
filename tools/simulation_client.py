import sys
from typing import Any
from base64 import b64encode

from socketio import Client

client = Client()


@client.event
def connect():
    print("connected")
    client.emit("simulation_start", {"motors": {"A": "large", "B": "medium"}, "sensors": {"1": "sensors.Ultrasound"}})


@client.event
def disconnect():
    print("disconnected")
    exit(1)


def simulation_update(response: Any) -> None:
    print(response)

def simulation_created(response: Any) -> None:
    print(response)
    while True:
        arguments = input("Choice: ").split(" ")
        if arguments[0] == "":
            arguments = []

        if len(arguments) == 0:
            client.emit("simulation_step", callback=simulation_update)
        elif len(arguments) == 1 and arguments[0].isdigit():
            client.emit("simulation_step", int(arguments[0]), callback=simulation_update)
        else:
            parameters = {}
            for parameter in arguments[1:]:
                key, value = parameter.split("=")
                parameters[key] = value
            client.emit("simulation_trigger_event", {"event": arguments[0], "parameters": parameters})

def main(project_path: str) -> None:
    print("=" * 80)
    print("This is a super simple and bare-bones simulation client.\n")
    print("* Enter an event to trigger, along with its parameters")
    print("* Press enter without any input to step once")
    print("* Enter a number and press enter to step multiple steps")
    print("* Press CTRL+C")
    print()
    print("Examples:")
    print("buttonEnter event=\"ButtonEvent.Pressed\" button=\"brick.buttonEnter\"")
    print("touchEvent event=\"ButtonEvent.Pressed\" sensor=\"sensors.touch1\"")
    print("10")
    print("<empty>\n")
    print("=" * 80 + "\n\n")

    client.connect('http://localhost:3773')

    with open(sys.argv[1], "rb") as file:
        data = file.read()
        client.emit("simulation_create", data, callback=simulation_created)


if __name__ == '__main__':
    main(sys.argv[1])
