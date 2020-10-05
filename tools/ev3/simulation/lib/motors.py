import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch, BranchLock
from tools.ev3.simulation.lib.utilities import call_handler, evaluate_value


@call_handler("motorRun")
def handle_motor_run(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor = block.fields["motor"].value
    speed = evaluate_value(block.values["speed"])
    logging.debug("Run motor '{}' with speed {}".format(motor, speed))


@call_handler("motorSchedule")
def handle_motor_schedule(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor = block.fields["motor"].value
    unit = block.fields["unit"].value
    speed = evaluate_value(block.values["speed"])
    value = evaluate_value(block.values["value"])
    logging.debug("Setting motor schedule motor={} unit={} speed={} value={}".format(motor, unit, speed, value))


@call_handler("motorPairTank")
def handle_motor_pair_tank(runtime: Runtime, block: Block, branch: Branch) -> None:
    motors = block.fields["motors"].value
    speed_left = block.values["speedLeft"].shadow.fields["speed"].value
    speed_right = block.values["speedRight"].shadow.fields["speed"].value
    logging.debug("Tanking motors motors={} speed_left={} speed_right={}".format(motors, speed_left, speed_right))


@call_handler("motorPairSteer")
def handle_motor_pair_steer(runtime: Runtime, block: Block, branch: Branch) -> None:
    chassis = block.fields["chassis"].value
    turn_ratio = block.values["turnRatio"].shadow.fields["turnratio"].value
    speed = block.values["speed"].shadow.fields["speed"].value
    logging.debug("Steering motors chassis={} turn_ratio={} speed={}".format(chassis, turn_ratio, speed))


@call_handler("motorPauseUntilRead")
def handle_motor_pause_until_read(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor = block.fields["motor"].value
    logging.debug("Pausing until read motor={}".format(motor))


@call_handler("motorStop")
def handle_motor_stop(runtime: Runtime, block: Block, branch: Branch) -> None:
    motors = block.fields["motors"].value
    logging.debug("Stopping motors={}".format(motors))


@call_handler("motorReset")
def handle_motor_reset(runtime: Runtime, block: Block, branch: Branch) -> None:
    motors = block.fields["motors"].value
    logging.debug("Resetting motors={}".format(motors))


@call_handler("motorStopAll")
def handle_motor_stop_all(runtime: Runtime, block: Block, branch: Branch) -> None:
    logging.debug("Stopping all motors")


@call_handler("motorResetAll")
def handle_motor_reset_all(runtime: Runtime, block: Block, branch: Branch) -> None:
    logging.debug("Resetting all motors")


@call_handler("motorClearCount")
def handle_motor_clear_count(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor = block.fields["motor"].value
    logging.debug("Clearing count for motor={}".format(motor))


@call_handler("outputMotorSetBrakeMode")
def handle_output_motor_set_brake_mode(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor = block.fields["motor"].value
    mode = block.values["brake"].shadow.fields["on"].value
    logging.debug("Setting motor brake mode motor={} mode={}".format(motor, mode))
