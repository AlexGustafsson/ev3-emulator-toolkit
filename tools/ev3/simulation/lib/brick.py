import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch
from tools.ev3.simulation.lib.utilities import call_handler, evaluate_value
from tools.ev3.simulation.brick import StatusLightPattern


@call_handler("brickShowPorts")
def handle_brick_show_ports(runtime: Runtime, block: Block, branch: Branch) -> None:
    logging.debug("Show brick ports")


@call_handler("setLights")
def handle_set_lights(runtime: Runtime, block: Block, branch: Branch) -> None:
    pattern = evaluate_value(block.values["pattern"])
    runtime.globals["brick"].set_status_light_pattern(StatusLightPattern(pattern))


@call_handler("screenShowImage")
def handle_screen_show_image(runtime: Runtime, block: Block, branch: Branch) -> None:
    image = evaluate_value(block.values["image"])
    logging.debug("Showing image {}".format(image))


@call_handler("screenPrint")
def handle_screen_print(runtime: Runtime, block: Block, branch: Branch) -> None:
    text = evaluate_value(block.values["text"])
    line = evaluate_value(block.values["line"])
    runtime.globals["brick"].clear_screen(line=line)
    runtime.globals["brick"].print(text, line=line)


@call_handler("screenShowNumber")
def handle_screen_show_number(runtime: Runtime, block: Block, branch: Branch) -> None:
    name = evaluate_value(block.values["name"])
    line = evaluate_value(block.values["line"])
    runtime.globals["brick"].clear_screen(line=line)
    runtime.globals["brick"].print("{}={}".format(name, text), line=0)


@call_handler("screenShowValue")
def handle_screen_show_value(runtime: Runtime, block: Block, branch: Branch) -> None:
    name = evaluate_value(block.values["name"])
    line = evaluate_value(block.values["line"])
    text = evaluate_value(block.values["text"])
    runtime.globals["brick"].clear_screen(line=line)
    runtime.globals["brick"].print("{}={}".format(name, text), line=line)


@call_handler("screenClearScreen")
def handle_screen_clear_screen(runtime: Runtime, block: Block, branch: Branch) -> None:
    runtime.globals["brick"].clear_screen()


@call_handler("moodShow")
def handle_mood_show(runtime: Runtime, block: Block, branch: Branch) -> None:
    mood = block.values["mood"].shadow.fields["mood"].value
    logging.debug("Showing mood '{}'".format(mood))


@call_handler("buttonEvent")
def handle_button_event(runtime: Runtime, block: Block, branch: Branch) -> None:
    button = block.fields["button"].value
    event = block.fields["event"].value
    handler = block.statements["HANDLER"]
    if handler is None:
        return
    runtime.register_event_handler(block.type, handler, button=button, event=event)
