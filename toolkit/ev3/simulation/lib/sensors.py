import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from toolkit.ev3.simulation.block.block import Block, BlockValue
from toolkit.ev3.simulation.runtime import Runtime, Branch, Event
from toolkit.ev3.simulation.lib.utilities import call_handler, evaluate_value


log = logging.getLogger(__name__)


@call_handler("buttonWaitUntil")
def handle_button_wait_until(runtime: Runtime, block: Block, branch: Branch) -> None:
    button = block.fields["button"].value
    event = block.fields["event"].value
    branch.lock = Event(event="buttonEvent", parameters={"button": button, "event": event})
    log.debug("Locking branch, waiting for event {}".format(branch.lock))


@call_handler("colorpauseUntilColorDetectedDetected")
def handle_colorpause_until_color_detected_detected(runtime: Runtime, block: Block, branch: Branch) -> None:
    color = evaluate_value(block.values["color"])
    sensor = block.fields["this"].value
    branch.lock = Event(event="colorOnColorDetected", parameters={"color": color, "sensor": sensor})
    log.debug("Locking branch, waiting for event {}".format(branch.lock))


@call_handler("colorPauseUntilLightDetected")
def handle_color_pause_until_light_detected(runtime: Runtime, block: Block, branch: Branch) -> None:
    #  {'type': 'colorPauseUntilLightDetected', 'values': {}, 'fields': {'this': BlockField(name='this', id=None, variable_type=None, value='sensors.color3'), 'mode': BlockField(name='mode', id=None, variable_type=None, value='LightIntensityMode.Reflected'), 'condition': BlockField(name='condition', id=None, variable_type=None, value='Light.Dark')}, 'statements': {}}
    mode = block.fields["mode"].value
    sensor = block.fields["this"].value
    branch.lock = Event(event="colorOnLightDetected", parameters={"mode": mode, "sensor": sensor})
    log.debug("Locking branch, waiting for event {}".format(branch.lock))


@call_handler("ultrasonicWait")
def handle_ultrasonic_wait(runtime: Runtime, block: Block, branch: Branch) -> None:
    sensor = block.fields["this"].value
    event = block.fields["event"].value
    branch.lock = Event(event="ultrasonicOn", parameters={"event": event, "sensor": sensor})
    log.debug("Locking branch, waiting for event {}".format(branch.lock))


@call_handler("touchWaitUntil")
def handle_touch_wait_until(runtime: Runtime, block: Block, branch: Branch) -> None:
    sensor = block.fields["this"].value
    event = block.fields["event"].value
    branch.lock = Event(event="touchEvent", parameters={"event": event, "sensor": sensor})
    log.debug("Locking branch, waiting for event {}".format(branch.lock))
