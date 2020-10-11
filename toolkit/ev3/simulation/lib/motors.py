import sys
import logging
import re
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional, Tuple
from inspect import getmembers, ismethod

from toolkit.ev3.simulation.block.block import Block, BlockValue
from toolkit.ev3.simulation.runtime import Runtime, Branch
from toolkit.ev3.simulation.lib.utilities import call_handler, evaluate_value


def parse_motor_label(label: str) -> List[Tuple[str, str]]:
    if (label.split(".")[0] != "motors" and label.split(".")[0] != "motor") or "." not in label:
        raise Exception("Got unsupported motor label '{}'".format(label))

    type = ""
    ports = ""
    for character in label.split(".")[1]:
        if character == character.lower():
            if ports == "":
                type += character
            else:
                raise Exception("Got corrupt motor label '{}'".format(label))
        else:
            ports += character

    if len(ports) == 0:
        raise Exception("Got bad motor label '{}' - missing ports".format(label))

    return [(port, type) for port in ports]


@call_handler("motorRun")
def handle_motor_run(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor_label = block.fields["motor"].value
    speed = evaluate_value(block.values["speed"])
    for port, type in parse_motor_label(motor_label):
        runtime.globals["brick"].get_motor(port, type).set_speed(speed)


@call_handler("motorSchedule")
def handle_motor_schedule(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor_label = block.fields["motor"].value
    unit = block.fields["unit"].value
    speed = evaluate_value(block.values["speed"])
    value = evaluate_value(block.values["value"])
    for port, type in parse_motor_label(motor_label):
        runtime.globals["brick"].get_motor(port, type).set_schedule(unit, speed, value)


@call_handler("motorPairTank")
def handle_motor_pair_tank(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor_label = block.fields["motors"].value
    speed_left = block.values["speedLeft"].shadow.fields["speed"].value
    speed_right = block.values["speedRight"].shadow.fields["speed"].value
    # TODO: Implement

@call_handler("motorPairSteer")
def handle_motor_pair_steer(runtime: Runtime, block: Block, branch: Branch) -> None:
    chassis = block.fields["chassis"].value
    turn_ratio = block.values["turnRatio"].shadow.fields["turnratio"].value
    speed = block.values["speed"].shadow.fields["speed"].value
    # TODO: Implement

@call_handler("motorPauseUntilRead")
def handle_motor_pause_until_read(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor_label = block.fields["motor"].value
    # TODO: Implement


@call_handler("motorStop")
def handle_motor_stop(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor_label = block.fields["motors"].value
    for port, type in parse_motor_label(motor_label):
        runtime.globals["brick"].get_motor(port, type).stop()


@call_handler("motorReset")
def handle_motor_reset(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor_label = block.fields["motors"].value
    for port, type in parse_motor_label(motor_label):
        runtime.globals["brick"].get_motor(port, type).reset()


@call_handler("motorStopAll")
def handle_motor_stop_all(runtime: Runtime, block: Block, branch: Branch) -> None:
    for motor in runtime.globals["brick"].motors.values():
        if motor is not None:
            motor.stop()


@call_handler("motorResetAll")
def handle_motor_reset_all(runtime: Runtime, block: Block, branch: Branch) -> None:
    for motor in runtime.globals["brick"].motors.values():
        if motor is not None:
            motor.reset()


@call_handler("motorClearCount")
def handle_motor_clear_count(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor_label = block.fields["motor"].value
    for port, type in parse_motor_label(motor_label):
        runtime.globals["brick"].get_motor(port, type).clear_count()


@call_handler("outputMotorSetBrakeMode")
def handle_output_motor_set_brake_mode(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor_label = block.fields["motor"].value
    mode = block.values["brake"].shadow.fields["on"].value
    for port, type in parse_motor_label(motor_label):
        runtime.globals["brick"].get_motor(port, type).set_brake_mode(mode)
