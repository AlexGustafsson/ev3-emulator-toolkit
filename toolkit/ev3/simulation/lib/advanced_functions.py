import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from toolkit.ev3.simulation.block.block import Block, BlockValue
from toolkit.ev3.simulation.runtime import Runtime, Branch
from toolkit.ev3.simulation.lib.utilities import call_handler, evaluate_value

log = logging.getLogger(__name__)


@call_handler("procedures_defnoreturn")
def handle_procedures_defnoreturn(runtime: Runtime, block: Block, branch: Branch) -> None:
    name = block.fields["NAME"].value
    # TODO: Implement params
    params = block.fields["PARAMS"].value
    handler = block.statements["STACK"]
    runtime.register_function(name, handler)


@call_handler("procedures_callnoreturn")
def handle_procedures_callnoreturn(runtime: Runtime, block: Block, branch: Branch) -> None:
    name = block.fields["NAME"].value
    # TODO: Implement params
    runtime.call_function(name)
