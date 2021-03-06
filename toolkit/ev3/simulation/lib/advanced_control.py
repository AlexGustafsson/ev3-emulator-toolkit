import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from toolkit.ev3.simulation.block.block import Block, BlockValue
from toolkit.ev3.simulation.runtime import Runtime, Branch
from toolkit.ev3.simulation.lib.utilities import call_handler, evaluate_value


log = logging.getLogger(__name__)


@call_handler("controlRunInParallel")
def handle_control_run_in_parallel(runtime: Runtime, block: Block, branch: Branch) -> None:
    runtime.add_branch(block.statements["HANDLER"])


@call_handler("controlWaitUs")
def handle_control_wait_us(runtime: Runtime, block: Block, branch: Branch) -> None:
    #  {'type': 'control_wait_us', 'values': {'micros': BlockValue(name='micros', shadow=BlockShadow(type='math_number', fields={'NUM': BlockField(name='NUM', id=None, variable_type=None, value='4')}))}, 'fields': {}, 'statements': {}}
    us = evaluate_value(block.values["micros"])
    # TODO: Actually implement lock
    branch.lock = Event(event="interrupt", parameters={})
    log.debug("Sleeping for {}μs".format(us))
