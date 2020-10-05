import sys
import logging
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod

from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch, BranchLock

__handlers: Dict[str, Callable[..., Any]] = {}


def call_handler(call: str) -> Callable[..., Any]:
    """Register a call handler."""
    def decorator(handler: Callable[..., Any]) -> Any:
        __handlers[call] = handler
        return handler
    return decorator


def get_all_handlers() -> Dict[str, Callable[... , Any]]:
    """Get all available call handlers."""
    return __handlers


def evaluate_value(value: BlockValue) -> Any:
    if value.shadow.type == "math_number":
        return int(value.shadow.fields["NUM"].value)
    elif value.shadow.type == "motorSpeedPicker":
        return int(value.shadow.fields["speed"].value)
    elif value.shadow.type == "timePicker":
        return int(value.shadow.fields["ms"].value)
    elif value.shadow.type == "text":
        return value.shadow.fields["TEXT"].value
    elif value.shadow.type == "colorEnumPicker":
        return value.shadow.fields["color"].value
    elif value.shadow.type == "screen_image_picker":
        return value.shadow.fields["image"].value
    elif value.shadow.type == "math_number_minmax":
        if "SLIDER" in value.shadow.fields:
            return int(value.shadow.fields["SLIDER"].value)
        else:
            logging.debug(value.shadow)
            raise Exception("Unimplemented math_number_minmax subtype '{}'".format(value.shadow.type))

    logging.debug(value.shadow)
    raise Exception("Unimplemented value type '{}'".format(value.shadow.type))


@call_handler("consoleLog")
def handle_console_log(runtime: Runtime, block: Block, branch: Branch) -> None:
    text = block.values["text"].shadow.fields["TEXT"].value
    text = "" if text is None else text
    logging.debug("Logging {}".format(text))
    print(text)


@call_handler("variablesSet")
def handle_variables_set(runtime: Runtime, block: Block, branch: Branch) -> None:
    id = block.fields["VAR"].id
    value = evaluate_value(block.values["VALUE"])
    logging.debug("Setting variable '{}' to '{}'".format(id, value))
    runtime.set_variable(id, value)


@call_handler("setLights")
def handle_set_lights(runtime: Runtime, block: Block, branch: Branch) -> None:
    pattern = block.fields["pattern"].value
    logging.debug("Setting lights to color {}".format(pattern))


@call_handler("motorRun")
def handle_motor_run(runtime: Runtime, block: Block, branch: Branch) -> None:
    motor = block.fields["motor"].value
    speed = evaluate_value(block.values["speed"])
    logging.debug("Run motor '{}' with speed {}".format(motor, speed))


@call_handler("moodShow")
def handle_mood_show(runtime: Runtime, block: Block, branch: Branch) -> None:
    mood = block.values["mood"].shadow.fields["mood"].value
    logging.debug("Showing mood '{}'".format(mood))


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


@call_handler("device_pause")
def handle_device_pause(runtime: Runtime, block: Block, branch: Branch) -> None:
    ms = evaluate_value(block.values["pause"])
    # TODO: Actually implement lock
    branch.lock = BranchLock(event="interrupt", args=tuple(), kwargs={})
    logging.debug("Sleeping for {}ms".format(ms))


@call_handler("pxtControlsFor")
def handle_pxt_controls_for(runtime: Runtime, block: Block, branch: Branch) -> None:
    # TODO: What does this do?
    pass


@call_handler("controlRunInParallel")
def handle_control_run_in_parallel(runtime: Runtime, block: Block, branch: Branch) -> None:
    runtime.add_branch(block.statements["HANDLER"])


@call_handler("controlWaitUs")
def handle_control_wait_us(runtime: Runtime, block: Block, branch: Branch) -> None:
    #  {'type': 'control_wait_us', 'values': {'micros': BlockValue(name='micros', shadow=BlockShadow(type='math_number', fields={'NUM': BlockField(name='NUM', id=None, variable_type=None, value='4')}))}, 'fields': {}, 'statements': {}}
    us = evaluate_value(block.values["micros"])
    # TODO: Actually implement lock
    branch.lock = BranchLock(event="interrupt", args=tuple(), kwargs={})
    logging.debug("Sleeping for {}μs".format(us))


@call_handler("consoleLogValue")
def handle_console_log_value(runtime: Runtime, block: Block, branch: Branch) -> None:
    name = evaluate_value(block.values["name"])
    value = evaluate_value(block.values["value"])
    logging.debug("Logging value {}={}".format(name, value))
    print("{}={}".format(name, value))


@call_handler("buttonWaitUntil")
def handle_button_wait_until(runtime: Runtime, block: Block, branch: Branch) -> None:
    button = block.fields["button"].value
    event = block.fields["event"].value
    branch.lock = BranchLock(event="buttonEvent", kwargs={"button": button, "event": event}, args=tuple())
    logging.debug("Waiting for event={} button={}".format(event, button))


@call_handler("colorpauseUntilColorDetectedDetected")
def handle_colorpause_until_color_detected_detected(runtime: Runtime, block: Block, branch: Branch) -> None:
    color = evaluate_value(block.values["color"])
    sensor = block.fields["this"].value
    branch.lock = BranchLock(event="colorOnColorDetected", kwargs={"color": color, "sensor": sensor}, args=tuple())
    logging.debug("Waiting for sensor {} to detect color {}".format(sensor, color))


@call_handler("colorPauseUntilLightDetected")
def handle_color_pause_until_light_detected(runtime: Runtime, block: Block, branch: Branch) -> None:
    #  {'type': 'colorPauseUntilLightDetected', 'values': {}, 'fields': {'this': BlockField(name='this', id=None, variable_type=None, value='sensors.color3'), 'mode': BlockField(name='mode', id=None, variable_type=None, value='LightIntensityMode.Reflected'), 'condition': BlockField(name='condition', id=None, variable_type=None, value='Light.Dark')}, 'statements': {}}
    mode = block.fields["mode"].value
    sensor = block.fields["this"].value
    branch.lock = BranchLock(event="colorOnLightDetected", kwargs={"mode": mode, "sensor": sensor}, args=tuple())
    logging.debug("Waiting for sensor {} to detect mode {}".format(sensor, mode))


@call_handler("ultrasonicWait")
def handle_ultrasonic_wait(runtime: Runtime, block: Block, branch: Branch) -> None:
    sensor = block.fields["this"].value
    event = block.fields["event"].value
    branch.lock = BranchLock(event="ultrasonicOn", kwargs={"event": event, "sensor": sensor}, args=tuple())
    logging.debug("Waiting for sensor {} to detect event {}".format(sensor, event))


@call_handler("touchWaitUntil")
def handle_touch_wait_until(runtime: Runtime, block: Block, branch: Branch) -> None:
    sensor = block.fields["this"].value
    event = block.fields["event"].value
    branch.lock = BranchLock(event="touchEvent", kwargs={"event": event, "sensor": sensor}, args=tuple())
    logging.debug("Waiting for sensor {} to detect event {}".format(sensor, event))


@call_handler("screenShowImage")
def handle_screen_show_image(runtime: Runtime, block: Block, branch: Branch) -> None:
    image = evaluate_value(block.values["image"])
    logging.debug("Showing image {}".format(image))


@call_handler("screenPrint")
def handle_screen_print(runtime: Runtime, block: Block, branch: Branch) -> None:
    text = evaluate_value(block.values["text"])
    line = evaluate_value(block.values["line"])
    logging.debug("Printing text={} on line={}".format(text, line))


@call_handler("screenShowNumber")
def handle_screen_show_number(runtime: Runtime, block: Block, branch: Branch) -> None:
    name = evaluate_value(block.values["name"])
    line = evaluate_value(block.values["line"])
    logging.debug("Printing name={} on line={}".format(name, line))


@call_handler("screenShowValue")
def handle_screen_show_value(runtime: Runtime, block: Block, branch: Branch) -> None:
    #  {'type': 'screenShowValue', 'values': {'name': BlockValue(name='name', shadow=BlockShadow(type='text', fields={'TEXT': BlockField(name='TEXT', id=None, variable_type=None, value=None)})), 'text': BlockValue(name='text', shadow=BlockShadow(type='math_number', fields={'NUM': BlockField(name='NUM', id=None, variable_type=None, value='0')})), 'line': BlockValue(name='line', shadow=BlockShadow(type='math_number_minmax', fields={'SLIDER': BlockField(name='SLIDER', id=None, variable_type=None, value='1')}))}, 'fields': {}, 'statements': {}}
    name = evaluate_value(block.values["name"])
    text = evaluate_value(block.values["text"])
    line = evaluate_value(block.values["line"])
    logging.debug("Printing {}={} on line={}".format(name, text, line))


@call_handler("brickShowPorts")
def handle_brick_show_ports(runtime: Runtime, block: Block, branch: Branch) -> None:
    logging.debug("Show brick ports")


@call_handler("screenClearScreen")
def handle_screen_clear_screen(runtime: Runtime, block: Block, branch: Branch) -> None:
    logging.debug("Clearing screen")
