import os
import logging
from typing import Tuple, Callable, Any

from tools.pxt.project import Project
from tools.ev3.simulation.block.source import BlockSource
from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime

PXT_START_BLOCK = "pxt-on-start"

class Simulator:
    def __init__(self, project: Project) -> None:
        self.__project = project

    @property
    def project(self) -> Project:
        """The project."""
        return self.__project

    def __handle_console_log(self, runtime: Runtime, block: Block) -> None:
        text = block.values["text"].shadow.fields["TEXT"].value
        logging.debug("Logging {}".format(text))
        print(text)

    def __evaluate_value(self, value: BlockValue) -> Any:
        if value.shadow.type == "math_number":
            return int(value.shadow.fields["NUM"].value)
        raise Exception("Unimplemented value type '{}'".format(value.shadow.type))

    def __handle_variables_set(self, runtime: Runtime, block: Block) -> None:
        id = block.fields["VAR"].id
        value = self.__evaluate_value(block.values["VALUE"])
        logging.debug("Setting variable '{}' to '{}'".format(id, value))
        runtime.set_variable(id, value)

    def __handle_set_lights(self, runtime: Runtime, block: Block) -> None:
        pattern = block.fields["pattern"].value
        logging.debug("Setting lights to color {}".format(pattern))

    def __handle_motor_run(self, runtime: Runtime, block: Block) -> None:
        motor = block.fields["motor"].value
        speed = int(block.values["speed"].shadow.fields["speed"].value)
        logging.debug("Run motor '{}' with speed {}".format(motor, speed))


    def __handle_mood_show(self, runtime: Runtime, block: Block) -> None:
        mood = block.values["mood"].shadow.fields["mood"].value
        logging.debug("Showing mood '{}'".format(mood))

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

        runtime.trigger_event("pxt-on-start")
        while runtime.current_branch is not None:
            runtime.step()
