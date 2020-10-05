import sys
import logging
import os
from functools import wraps
from typing import Dict, Set, List, Callable, Any, Optional
from inspect import getmembers, ismethod
from glob import glob

from tools.ev3.simulation.block.block import BlockValue

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
