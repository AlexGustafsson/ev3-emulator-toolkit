import os
import logging
import time
from typing import Tuple, Callable, Any

from tools.pxt.project import Project
from tools.ev3.simulation.block.source import BlockSource
from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch, BranchLock

PXT_START_BLOCK = "pxt-on-start"

class Simulator:
    def __init__(self, project: Project) -> None:
        self.__project = project

    @property
    def project(self) -> Project:
        """The project."""
        return self.__project

    def __evaluate_value(self, value: BlockValue) -> Any:
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

    def __handle_console_log(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        text = block.values["text"].shadow.fields["TEXT"].value
        text = "" if text is None else text
        logging.debug("Logging {}".format(text))
        print(text)

    def __handle_variables_set(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        id = block.fields["VAR"].id
        value = self.__evaluate_value(block.values["VALUE"])
        logging.debug("Setting variable '{}' to '{}'".format(id, value))
        runtime.set_variable(id, value)

    def __handle_set_lights(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        pattern = block.fields["pattern"].value
        logging.debug("Setting lights to color {}".format(pattern))

    def __handle_motor_run(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        motor = block.fields["motor"].value
        speed = self.__evaluate_value(block.values["speed"])
        logging.debug("Run motor '{}' with speed {}".format(motor, speed))

    def __handle_mood_show(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        mood = block.values["mood"].shadow.fields["mood"].value
        logging.debug("Showing mood '{}'".format(mood))

    def __handle_motor_schedule(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        motor = block.fields["motor"].value
        unit = block.fields["unit"].value
        speed = self.__evaluate_value(block.values["speed"])
        value = self.__evaluate_value(block.values["value"])
        logging.debug("Setting motor schedule motor={} unit={} speed={} value={}".format(motor, unit, speed, value))

    def __handle_motor_pair_tank(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        motors = block.fields["motors"].value
        speed_left = block.values["speedLeft"].shadow.fields["speed"].value
        speed_right = block.values["speedRight"].shadow.fields["speed"].value
        logging.debug("Tanking motors motors={} speed_left={} speed_right={}".format(motors, speed_left, speed_right))

    def __handle_motor_pair_steer(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        chassis = block.fields["chassis"].value
        turn_ratio = block.values["turnRatio"].shadow.fields["turnratio"].value
        speed = block.values["speed"].shadow.fields["speed"].value
        logging.debug("Steering motors chassis={} turn_ratio={} speed={}".format(chassis, turn_ratio, speed))

    def __handle_motor_pause_until_read(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        motor = block.fields["motor"].value
        logging.debug("Pausing until read motor={}".format(motor))

    def __handle_motor_stop(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        motors = block.fields["motors"].value
        logging.debug("Stopping motors={}".format(motors))

    def __handle_motor_reset(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        motors = block.fields["motors"].value
        logging.debug("Resetting motors={}".format(motors))

    def __handle_motor_stop_all(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        logging.debug("Stopping all motors")

    def __handle_motor_reset_all(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        logging.debug("Resetting all motors")

    def __handle_motor_clear_count(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        motor = block.fields["motor"].value
        logging.debug("Clearing count for motor={}".format(motor))

    def __handle_output_motor_set_brake_mode(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        motor = block.fields["motor"].value
        mode = block.values["brake"].shadow.fields["on"].value
        logging.debug("Setting motor brake mode motor={} mode={}".format(motor, mode))

    def __handle_device_pause(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        ms = self.__evaluate_value(block.values["pause"])
        # TODO: Actually implement lock
        branch.lock = BranchLock(event="interrupt", args=tuple(), kwargs={})
        logging.debug("Sleeping for {}ms".format(ms))

    def __handle_pxt_controls_for(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        # TODO: What does this do?
        pass

    def __handle_control_run_in_parallel(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        runtime.add_branch(block.statements["HANDLER"])

    def __handle_control_wait_us(self, runtime: Runtime, block: Block, branch: Branch) -> None:
		#  {'type': 'control_wait_us', 'values': {'micros': BlockValue(name='micros', shadow=BlockShadow(type='math_number', fields={'NUM': BlockField(name='NUM', id=None, variable_type=None, value='4')}))}, 'fields': {}, 'statements': {}}
        us = self.__evaluate_value(block.values["micros"])
        # TODO: Actually implement lock
        branch.lock = BranchLock(event="interrupt", args=tuple(), kwargs={})
        logging.debug("Sleeping for {}μs".format(us))

    def __handle_console_log_value(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        name = self.__evaluate_value(block.values["name"])
        value = self.__evaluate_value(block.values["value"])
        logging.debug("Logging value {}={}".format(name, value))
        print("{}={}".format(name, value))

    def __handle_button_wait_until(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        button = block.fields["button"].value
        event = block.fields["event"].value
        branch.lock = BranchLock(event="buttonEvent", kwargs={"button": button, "event": event}, args=tuple())
        logging.debug("Waiting for event={} button={}".format(event, button))

    def __handle_colorpause_until_color_detected_detected(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        color = self.__evaluate_value(block.values["color"])
        sensor = block.fields["this"].value
        branch.lock = BranchLock(event="colorOnColorDetected", kwargs={"color": color, "sensor": sensor}, args=tuple())
        logging.debug("Waiting for sensor {} to detect color {}".format(sensor, color))

    def __handle_color_pause_until_light_detected(self, runtime: Runtime, block: Block, branch: Branch) -> None:
		#  {'type': 'colorPauseUntilLightDetected', 'values': {}, 'fields': {'this': BlockField(name='this', id=None, variable_type=None, value='sensors.color3'), 'mode': BlockField(name='mode', id=None, variable_type=None, value='LightIntensityMode.Reflected'), 'condition': BlockField(name='condition', id=None, variable_type=None, value='Light.Dark')}, 'statements': {}}
        mode = block.fields["mode"].value
        sensor = block.fields["this"].value
        branch.lock = BranchLock(event="colorOnLightDetected", kwargs={"mode": mode, "sensor": sensor}, args=tuple())
        logging.debug("Waiting for sensor {} to detect mode {}".format(sensor, mode))

    def __handle_ultrasonic_wait(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        sensor = block.fields["this"].value
        event = block.fields["event"].value
        branch.lock = BranchLock(event="ultrasonicOn", kwargs={"event": event, "sensor": sensor}, args=tuple())
        logging.debug("Waiting for sensor {} to detect event {}".format(sensor, event))

    def __handle_touch_wait_until(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        sensor = block.fields["this"].value
        event = block.fields["event"].value
        branch.lock = BranchLock(event="touchEvent", kwargs={"event": event, "sensor": sensor}, args=tuple())
        logging.debug("Waiting for sensor {} to detect event {}".format(sensor, event))

    def __handle_screen_show_image(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        image = self.__evaluate_value(block.values["image"])
        logging.debug("Showing image {}".format(image))

    def __handle_screen_print(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        text = self.__evaluate_value(block.values["text"])
        line = self.__evaluate_value(block.values["line"])
        logging.debug("Printing text={} on line={}".format(text, line))

    def __handle_screen_show_number(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        name = self.__evaluate_value(block.values["name"])
        line = self.__evaluate_value(block.values["line"])
        logging.debug("Printing name={} on line={}".format(name, line))

    def __handle_screen_show_value(self, runtime: Runtime, block: Block, branch: Branch) -> None:
		#  {'type': 'screenShowValue', 'values': {'name': BlockValue(name='name', shadow=BlockShadow(type='text', fields={'TEXT': BlockField(name='TEXT', id=None, variable_type=None, value=None)})), 'text': BlockValue(name='text', shadow=BlockShadow(type='math_number', fields={'NUM': BlockField(name='NUM', id=None, variable_type=None, value='0')})), 'line': BlockValue(name='line', shadow=BlockShadow(type='math_number_minmax', fields={'SLIDER': BlockField(name='SLIDER', id=None, variable_type=None, value='1')}))}, 'fields': {}, 'statements': {}}
        name = self.__evaluate_value(block.values["name"])
        text = self.__evaluate_value(block.values["text"])
        line = self.__evaluate_value(block.values["line"])
        logging.debug("Printing {}={} on line={}".format(name, text, line))

    def __handle_brick_show_ports(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        logging.debug("Show brick ports")

    def __handle_screen_clear_screen(self, runtime: Runtime, block: Block, branch: Branch) -> None:
        logging.debug("Clearing screen")

    def __trigger_forever(self, runtime) -> None:
        def trigger():
            runtime.trigger_event("forever", trigger)
        trigger()

    def run(self) -> None:
        logging.info("Extracting and parsing main source")
        files = dict(self.__project.files)
        main = BlockSource(files["main.blocks"])
        runtime = Runtime(main)

        runtime.register_handler("console_log", self.__handle_console_log)
        runtime.register_handler("variables_set", self.__handle_variables_set)
        runtime.register_handler("setLights", self.__handle_set_lights)
        runtime.register_handler("motorRun", self.__handle_motor_run)
        runtime.register_handler("moodShow", self.__handle_mood_show)
        runtime.register_handler("motorSchedule", self.__handle_motor_schedule)
        runtime.register_handler("motorPairTank", self.__handle_motor_pair_tank)
        runtime.register_handler("motorPairSteer", self.__handle_motor_pair_steer)
        runtime.register_handler("motorPauseUntilRead", self.__handle_motor_pause_until_read)
        runtime.register_handler("motorStop", self.__handle_motor_stop)
        runtime.register_handler("motorReset", self.__handle_motor_reset)
        runtime.register_handler("motorStopAll", self.__handle_motor_stop_all)
        runtime.register_handler("motorResetAll", self.__handle_motor_reset_all)
        runtime.register_handler("motorClearCount", self.__handle_motor_clear_count)
        runtime.register_handler("outputMotorSetBrakeMode", self.__handle_output_motor_set_brake_mode)
        runtime.register_handler("device_pause", self.__handle_device_pause)
        runtime.register_handler("pxt_controls_for", self.__handle_pxt_controls_for)
        runtime.register_handler("control_run_in_parallel", self.__handle_control_run_in_parallel)
        runtime.register_handler("control_wait_us", self.__handle_control_wait_us)
        runtime.register_handler("console_log_value", self.__handle_console_log_value)
        runtime.register_handler("buttonWaitUntil", self.__handle_button_wait_until)
        runtime.register_handler("colorpauseUntilColorDetectedDetected", self.__handle_colorpause_until_color_detected_detected)
        runtime.register_handler("colorPauseUntilLightDetected", self.__handle_color_pause_until_light_detected)
        runtime.register_handler("ultrasonicWait", self.__handle_ultrasonic_wait)
        runtime.register_handler("touchWaitUntil", self.__handle_touch_wait_until)
        runtime.register_handler("screen_show_image", self.__handle_screen_show_image)
        runtime.register_handler("screen_print", self.__handle_screen_print)
        runtime.register_handler("screenShowNumber", self.__handle_screen_show_number)
        runtime.register_handler("screenShowValue", self.__handle_screen_show_value)
        runtime.register_handler("brickShowPorts", self.__handle_brick_show_ports)
        runtime.register_handler("screen_clear_screen", self.__handle_screen_clear_screen)

        runtime.trigger_event("pxt-on-start")
        forever = runtime.trigger_event("forever")

        # For testing only, not meant for production:
        runtime.trigger_event("buttonEvent")
        runtime.trigger_event("colorOnColorDetected")
        runtime.trigger_event("colorOnLightDetected")
        runtime.trigger_event("ultrasonicOn")
        runtime.trigger_event("touchEvent")

        while runtime.current_branch is not None:
            result = runtime.step()
            if result.completed_branch and result.processed_branch == forever:
                forever = runtime.trigger_event("forever")
            time.sleep(0.2)
