import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch, BranchLock
from tools.ev3.simulation.lib.utilities import call_handler, evaluate_value


@call_handler("variablesSet")
def handle_variables_set(runtime: Runtime, block: Block, branch: Branch) -> None:
    id = block.fields["VAR"].id
    value = evaluate_value(block.values["VALUE"])
    logging.debug("Setting variable '{}' to '{}'".format(id, value))
    runtime.set_variable(id, value)
