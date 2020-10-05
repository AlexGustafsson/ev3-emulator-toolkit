import os
import logging
import time
from typing import Tuple, Callable, Any

from tools.pxt.project import Project
from tools.ev3.simulation.block.source import BlockSource
from tools.ev3.simulation.block.block import Block, BlockValue
from tools.ev3.simulation.runtime import Runtime, Branch, BranchLock
from tools.ev3.simulation.lib.utilities import get_all_handlers


class Simulator:
    def __init__(self, project: Project) -> None:
        self.__project = project

    @property
    def project(self) -> Project:
        """The project."""
        return self.__project

    def __trigger_forever(self, runtime) -> None:
        def trigger():
            runtime.trigger_event("forever", trigger)
        trigger()

    def run(self) -> None:
        logging.info("Extracting and parsing main source")
        files = dict(self.__project.files)
        main = BlockSource(files["main.blocks"])
        runtime = Runtime(main)

        # Register all built-in calls
        for call, handler in get_all_handlers().items():
            runtime.register_handler(call, handler)

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
