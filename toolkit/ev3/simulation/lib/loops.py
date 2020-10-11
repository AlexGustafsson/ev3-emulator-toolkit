import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from toolkit.ev3.simulation.block.block import Block, BlockValue
from toolkit.ev3.simulation.runtime import Runtime, Branch, Event
from toolkit.ev3.simulation.lib.utilities import call_handler, evaluate_value

log = logging.getLogger(__name__)


@call_handler("pxt-on-start")
def handle_pxt_on_start(runtime: Runtime, block: Block, branch: Branch) -> None:
    handler = block.statements["HANDLER"]
    if handler is None:
        return
    runtime.register_event_handler(block.type, handler)


@call_handler("pxtControlsFor")
def handle_pxt_controls_for(runtime: Runtime, block: Block, branch: Branch) -> None:
    # TODO: What does this do?
    pass


@call_handler("device_pause")
def handle_device_pause(runtime: Runtime, block: Block, branch: Branch) -> None:
    ms = evaluate_value(block.values["pause"])
    # TODO: Actually implement lock
    branch.lock = Event(event="interrupt", parameters={})
    log.debug("Sleeping for {}ms".format(ms))
