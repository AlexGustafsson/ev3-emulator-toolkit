import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch
from tools.ev3.simulation.lib.utilities import call_handler, evaluate_value

log = logging.getLogger(__name__)

@call_handler("pxtControlsFor")
def handle_pxt_controls_for(runtime: Runtime, block: Block, branch: Branch) -> None:
    # TODO: What does this do?
    pass

@call_handler("device_pause")
def handle_device_pause(runtime: Runtime, block: Block, branch: Branch) -> None:
    ms = evaluate_value(block.values["pause"])
    # TODO: Actually implement lock
    branch.lock = BranchLock(event="interrupt", args=tuple(), kwargs={})
    log.debug("Sleeping for {}ms".format(ms))
