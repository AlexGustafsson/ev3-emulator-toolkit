import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from toolkit.ev3.simulation.block.block import Block, BlockValue
from toolkit.ev3.simulation.runtime import Runtime, Branch
from toolkit.ev3.simulation.lib.utilities import call_handler, evaluate_value


log = logging.getLogger(__name__)


@call_handler("variablesSet")
def handle_variables_set(runtime: Runtime, block: Block, branch: Branch) -> None:
    id = block.fields["VAR"].id
    value = evaluate_value(block.values["VALUE"])
    log.debug("Setting variable '{}' to '{}'".format(id, value))
    runtime.set_variable(id, value)
