import os
import logging
import time
from typing import Tuple, Callable, Any, Optional

from tools.pxt.project import Project
from tools.ev3.simulation.block.source import BlockSource
from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch, StepResult
from tools.ev3.simulation.lib.utilities import get_all_handlers
from tools.ev3.simulation.brick import Brick, Motor


class Simulator:
    def __init__(self, project: Project) -> None:
        self.__project = project

        logging.info("Extracting and parsing main source")
        files = dict(self.__project.files)
        main = BlockSource(files["main.blocks"])
        self.__runtime = Runtime(main)

        # Register all built-in calls
        for call, handler in get_all_handlers().items():
            self.__runtime.register_handler(call, handler)

        # Create a brick and make it available to the runtime
        self.__brick = Brick(self.__runtime)
        self.__runtime.globals["brick"] = self.__brick

        # Branch for the special forever event
        self.__forever_branch: Branch

    @property
    def runtime(self) -> Runtime:
        """The runtime."""
        return self.__runtime

    @property
    def brick(self) -> Runtime:
        """The brick."""
        return self.__brick

    @property
    def project(self) -> Project:
        """The project."""
        return self.__project

    def __trigger_forever(self, runtime) -> None:
        def trigger():
            runtime.trigger_event("forever")
        trigger()

    def start(self) -> None:
        # Start the runtime after the handler setup
        self.__runtime.start()

        # Trigger the start event
        self.__runtime.trigger_event("pxt-on-start")

        # Start triggering the forever event
        self.__forever = self.__runtime.trigger_event("forever")

    def step(self) -> Optional[StepResult]:
        result = self.__runtime.step()
        if result is None:
            return

        # If the branch was a completed forever event, trigger it again
        if result.completed_branch and result.processed_branch == self.__forever:
            self.__forever = self.__runtime.trigger_event("forever")
        return result

    def run(self) -> None:
        while True:
            while self.__runtime.current_branch is not None:
                self.step()
                time.sleep(0.1)
            logging.debug("No branches left, waiting")
            time.sleep(0.5)
