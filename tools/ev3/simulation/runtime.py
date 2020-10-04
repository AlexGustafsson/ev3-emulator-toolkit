import logging
from typing import Dict, Set, List, Callable, Any
from queue import Queue

from tools.ev3.simulation.block.block import Block
from tools.ev3.simulation.block.source import BlockSource

class Runtime:
    def __init__(self, source: BlockSource) -> None:
        self.__source = source
        self.__variables: Dict[str, Any] = {}
        self.__event_handlers: Dict[str, Set[Block]] = {}

        self.__current_branch = None
        self.__branches: List[Block] = []

        self.__handlers: Dict[str, Callable[["Runtime", Block], None]] = {}

        # Register event handlers from source
        for block in source.blocks:
            for handler in block.statements.values():
                self.register_event_handler(block.type, handler)

        # Declare variables
        for id, _ in source.variables.items():
            self.__variables[id] = None

    @property
    def current_branch(self) -> int:
        """The current branch being processed."""
        return self.__current_branch

    @property
    def branches(self) -> List[Block]:
        """Currently available branches."""
        return self.__branches

    def set_variable(self, id: str, value: Any) -> None:
        """Set a variable by id."""
        self.__variables[id] = value

    def add_branch(self, block: Block) -> None:
        """Add a branch for evaluation."""
        self.__branches.append(block)
        if self.__current_branch is None:
            self.__current_branch = 0

    def trigger_event(self, event: str) -> None:
        """Trigger an event by name."""
        if event not in self.__event_handlers:
            logging.warning("No handlers registered for event '{}'. Events will be skipped".format(event))
            return

        for handler in self.__event_handlers[event]:
            self.add_branch(handler)
        logging.info("Triggered event '{}'".format(event))

    def register_event_handler(self, event: str, handler: Block) -> None:
        """Register a handler for an event by name."""
        if event not in self.__event_handlers:
            self.__event_handlers[event] = []
        self.__event_handlers[event].append(handler)
        logging.info("Registered event handler for event '{}'".format(event))

    def register_handler(self, type: str, handler: Callable[[Block], None]) -> None:
        """Register a handler for a type of call."""
        self.__handlers[type] = handler;

    def __invoke(self, block: Block) -> None:
        """Invoke a block call."""
        if block.type in self.__handlers:
            logging.info("Invoking block: {}".format(block.type))
            self.__handlers[block.type](self, block)
        else:
            raise Exception("No block handler registered for type '{}'".format(block.type))


    def step(self) -> None:
        """Execute one step."""
        if self.__current_branch is None:
            return

        current_block = self.__branches[self.__current_branch]

        # Process the call for the current branch
        self.__invoke(current_block)

        if current_block.next:
            # Move the branch forward
            self.__branches[self.__current_branch] = current_block.next
            # Move on to the next branch
            self.__current_branch = (self.__current_branch + 1) % len(self.__branches)
        else:
            # Remove the branch as it has been completed
            self.__branches.pop(self.__current_branch)
            # If the removed branch was the last, move on to the next branch
            # otherwise, the index will already be pointing to the next branch
            if (self.__current_branch == len(self.__branches)):
                self.__current_branch = 0
            # If there are no more branches, reset the pointer
            if (len(self.__branches) == 0):
                self.__current_branch = None
