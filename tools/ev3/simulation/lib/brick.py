import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch, BranchLock
from tools.ev3.simulation.lib.utilities import call_handler, evaluate_value


@call_handler("brickShowPorts")
def handle_brick_show_ports(runtime: Runtime, block: Block, branch: Branch) -> None:
    logging.debug("Show brick ports")


@call_handler("setLights")
def handle_set_lights(runtime: Runtime, block: Block, branch: Branch) -> None:
    pattern = block.fields["pattern"].value
    logging.debug("Setting lights to color {}".format(pattern))


@call_handler("screenShowImage")
def handle_screen_show_image(runtime: Runtime, block: Block, branch: Branch) -> None:
    image = evaluate_value(block.values["image"])
    logging.debug("Showing image {}".format(image))


@call_handler("screenPrint")
def handle_screen_print(runtime: Runtime, block: Block, branch: Branch) -> None:
    text = evaluate_value(block.values["text"])
    line = evaluate_value(block.values["line"])
    logging.debug("Printing text={} on line={}".format(text, line))


@call_handler("screenShowNumber")
def handle_screen_show_number(runtime: Runtime, block: Block, branch: Branch) -> None:
    name = evaluate_value(block.values["name"])
    line = evaluate_value(block.values["line"])
    logging.debug("Printing name={} on line={}".format(name, line))


@call_handler("screenShowValue")
def handle_screen_show_value(runtime: Runtime, block: Block, branch: Branch) -> None:
    #  {'type': 'screenShowValue', 'values': {'name': BlockValue(name='name', shadow=BlockShadow(type='text', fields={'TEXT': BlockField(name='TEXT', id=None, variable_type=None, value=None)})), 'text': BlockValue(name='text', shadow=BlockShadow(type='math_number', fields={'NUM': BlockField(name='NUM', id=None, variable_type=None, value='0')})), 'line': BlockValue(name='line', shadow=BlockShadow(type='math_number_minmax', fields={'SLIDER': BlockField(name='SLIDER', id=None, variable_type=None, value='1')}))}, 'fields': {}, 'statements': {}}
    name = evaluate_value(block.values["name"])
    text = evaluate_value(block.values["text"])
    line = evaluate_value(block.values["line"])
    logging.debug("Printing {}={} on line={}".format(name, text, line))


@call_handler("screenClearScreen")
def handle_screen_clear_screen(runtime: Runtime, block: Block, branch: Branch) -> None:
    logging.debug("Clearing screen")


@call_handler("moodShow")
def handle_mood_show(runtime: Runtime, block: Block, branch: Branch) -> None:
    mood = block.values["mood"].shadow.fields["mood"].value
    logging.debug("Showing mood '{}'".format(mood))
