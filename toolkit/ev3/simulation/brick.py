import json
from enum import Enum
from typing import Dict, Optional, List, Any, Union

from toolkit.ev3.simulation.runtime import Runtime


class Motor:
    def __init__(self, type: str) -> None:
        self.__type = type
        self.__speed = 0
        self.__angle = 0
        self.__count = 0

    @property
    def type(self) -> str:
        """Motor type."""
        return self.__type

    def to_dict(self) -> Dict[str, Union[str, int, bool, None]]:
        return {
            "type": self.__type,
            "speed": self.__speed,
            "angle": self.__angle,
            "count": self.__count
        }

    def set_speed(self, speed: int) -> None:
        """Set speed."""
        self.__speed = speed

    def set_schedule(self, unit, speed, value) -> None:
        """??"""

    def stop(self) -> None:
        """Stop the motor."""
        self.__speed = 0

    def reset(self) -> None:
        """Reset the motor."""
        self.__angle = 0

    def clear_count(self) -> None:
        """Clear the count."""
        self.__count = 0

    def set_brake_mode(self, mode: str) -> None:
        """Set brake mode."""
        # TODO: Implement

class Sensor:
    def __init__(self, type: str) -> None:
        pass

    def to_dict(self) -> Dict[str, Union[str, int, bool, None]]:
        return {}

class StatusLightPattern(str, Enum):
    ORANGE = "StatusLight.Orange"
    OFF = "StatusLight.Off"
    GREEN = "StatusLight.Green"
    RED = "StatusLight.Red"
    GREEN_FLASH = "StatusLight.GreenFlash"
    RED_FLASH = "StatusLight.RedFlash"
    ORANGE_FLASH = "StatusLight.OrangeFlash"
    GREEN_PULSE = "StatusLight.GreenPulse"
    RED_PULSE = "StatusLight.RedPulse"
    ORANGE_PULSE = "StatusLight.OrangePulse"

class Brick:
    def __init__(self, runtime: Runtime) -> None:
        self.__runtime = runtime

        self.__motors: Dict[str, Optional[Motor]] = {
            "A": None,
            "B": None,
            "C": None,
            "D": None
        }

        self.__sensors: Dict[str, Optional[Sensor]] = {
            "1": None,
            "2": None,
            "3": None,
            "4": None
        }

        self.__screen_width = 178
        self.__screen_height = 128
        self.__screen = [[False for x in range(self.__screen_width)] for y in range(self.__screen_height)]

        self.__status_light_pattern = StatusLightPattern.OFF

    @property
    def motors(self) -> Dict[str, Optional[Motor]]:
        return self.__motors

    @property
    def sensors(self) -> Dict[str, Optional[Sensor]]:
        return self.__sensors

    @property
    def screen(self) -> List[List[bool]]:
        return self.__screen

    @property
    def status_light_pattern(self) -> StatusLightPattern:
        return self.__status_light_pattern

    def to_dict(self) -> str:
        data = {
            "statusLightPattern": self.__status_light_pattern,
            "motors": {port: (None if motor is None else motor.to_dict()) for port, motor in self.__motors.items()},
            "sensors": {port: (None if sensor is None else sensor.to_dict()) for port, sensor in self.__sensors.items()},
        }
        return data

    def press_backspace(self) -> None:
        """Press the backspace key."""
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonEnter", event="ButtonEvent.Pressed")
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonEnter", event="ButtonEvent.Released")

    def press_up(self) -> None:
        """Press the up key."""
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonUp", event="ButtonEvent.Pressed")
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonUp", event="ButtonEvent.Released")

    def press_left(self) -> None:
        """Press the left key."""
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonLeft", event="ButtonEvent.Pressed")
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonLeft", event="ButtonEvent.Released")

    def press_enter(self) -> None:
        """Press the enter key."""
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonEnter", event="ButtonEvent.Pressed")
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonEnter", event="ButtonEvent.Released")

    def press_right(self) -> None:
        """Press the right key."""
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonRight", event="ButtonEvent.Pressed")
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonRight", event="ButtonEvent.Released")

    def press_down(self) -> None:
        """Press the down key."""
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonDown", event="ButtonEvent.Pressed")
        self.__runtime.trigger_event("buttonEvent", button="brick.buttonDown", event="ButtonEvent.Released")

    def print(self, text: str, line: int=None) -> None:
        """Print a string."""
        line = 0 if line is None else line
        # TODO: implement

    def clear_screen(self, line: int=None) -> None:
        """Clear the screen."""
        if line is None:
            self.__screen = [[False for x in range(self.__screen_width)] for y in range(self.__screen_height)]
        else:
            self.__screen[line] = [False for x in range(self.__screen_width)]

    def set_status_light_pattern(self, pattern: StatusLightPattern) -> None:
        self.__status_light_pattern = pattern

    def get_motor(self, port: str, type: str=None) -> None:
        """Ensure that a motor is connected."""
        if port not in self.__motors:
            raise Exception("No such motor port '{}'".format(port))
        if self.__motors[port] is None:
            raise Exception("No motor connected to port '{}'".format(port))
        if type is not None and type != self.__motors[port].type:
            raise Exception("Port mismatch - expected '{}' but got '{}'".format(self.__motors[port].type, type))
        return self.__motors[port]
