import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from toolkit.ev3.simulation.block.block import Block, BlockValue
from toolkit.ev3.simulation.runtime import Runtime, Branch
from toolkit.ev3.simulation.lib.utilities import call_handler, evaluate_value

log = logging.getLogger(__name__)


@call_handler("console_log")
def handle_console_log(runtime: Runtime, block: Block, branch: Branch) -> None:
    text = block.values["text"].shadow.fields["TEXT"].value
    text = "" if text is None else text
    log.debug("Logging {}".format(text))
    print(text)


@call_handler("consoleLogValue")
def handle_console_log_value(runtime: Runtime, block: Block, branch: Branch) -> None:
    name = evaluate_value(block.values["name"])
    value = evaluate_value(block.values["value"])
    log.debug("Logging value {}={}".format(name, value))
    print("{}={}".format(name, value))
