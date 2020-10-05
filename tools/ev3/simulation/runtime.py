import logging
import re
from typing import Dict, Set, List, Callable, Any, Optional
from queue import Queue
from dataclasses import dataclass

from tools.ev3.simulation.block.block import Block
from tools.ev3.simulation.block.source import BlockSource

@dataclass
class BranchLock:
    event: str
    args: List[Any]
    kwargs: Dict[str, Any]

    def __eq__(self, other: "BranchLock") -> bool:
        if other is None:
            return False

        if self.event != other.event:
            return False

        if len(self.args) != len(other.args):
            return False

        for i in range(len(self.args)):
            if self.args[i] != other.args[i]:
                return False

        if len(self.kwargs) != len(other.kwargs):
            return False

        for key, value in self.kwargs.items():
            if other.kwargs[key] != value:
                return False

@dataclass
class Branch:
    root: Block
    step: int
    current_block: Block
    parent_branch: Optional["Branch"]
    lock: BranchLock

@dataclass
class StepResult:
    processed_branch: Branch
    completed_branch: bool

class Runtime:
    def __init__(self, source: BlockSource) -> None:
        self.__source = source
        self.__variables: Dict[str, Any] = {}
        self.__event_handlers: Dict[str, Set[Block]] = {}

        self.__current_branch = None
        self.__branches: List[Branch] = []

        self.__handlers: Dict[str, Callable[["Runtime", Block, Branch], None]] = {}

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
    def branches(self) -> List[Branch]:
        """Currently available branches."""
        return self.__branches

    def set_variable(self, id: str, value: Any) -> None:
        """Set a variable by id."""
        self.__variables[id] = value

    def add_branch(self, block: Block, parent_branch: Branch = None) -> Branch:
        """Add a branch for evaluation."""
        branch = Branch(root=block, step=0, current_block=block, parent_branch=parent_branch, lock=None)
        self.__branches.append(branch)
        if self.__current_branch is None:
            self.__current_branch = 0
        return branch

    def trigger_event(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Trigger an event by name."""
        if event in self.__event_handlers:
            for handler in self.__event_handlers[event]:
                self.add_branch(handler)

        lock = BranchLock(event=event, args=args, kwargs=kwargs)
        for branch in self.__branches:
            if branch.lock == lock:
                logging.debug("Unlocked branch")
                branch.lock = None

        logging.info("Triggered event '{}'".format(event))

    def register_event_handler(self, event: str, handler: Block) -> None:
        """Register a handler for an event by name."""
        if event not in self.__event_handlers:
            self.__event_handlers[event] = []
        self.__event_handlers[event].append(handler)
        logging.info("Registered event handler for event '{}'".format(event))

    def register_handler(self, type: str, handler: Callable[[Block, Branch], None]) -> None:
        """Register a handler for a type of call."""
        self.__handlers[type] = handler;

    def __invoke(self, block: Block, branch: Branch) -> None:
        """Invoke a block call."""
        if block.type in self.__handlers:
            logging.info("Invoking block: {}".format(block.type))
            self.__handlers[block.type](self, block, branch)
        else:
            print("==/ To implement \==")
            print("def __handle_{}(self, runtime: Runtime, block: Block) -> None:".format(re.sub(r'(?<!^)(?=[A-Z])', '_', block.type).lower()))
            values = {
                "type": block.type,
                "values": block.values,
                "fields": block.fields,
                "statements": block.statements
            }
            print("\t\t# ", values)
            print('runtime.register_handler("{}", self.__handle_{})'.format(block.type, re.sub(r'(?<!^)(?=[A-Z])', '_', block.type).lower()))
            print("==\ To implement /==")
            raise Exception("No block handler registered for type '{}'".format(block.type))


    def step(self) -> StepResult:
        """Execute one step."""
        if self.__current_branch is None:
            return

        processed_branch = self.__branches[self.__current_branch]

        if processed_branch.lock is not None:
            logging.debug("Branch is locked")
            # Move on to the next branch
            self.__current_branch = (self.__current_branch + 1) % len(self.__branches)
            return StepResult(processed_branch=processed_branch, completed_branch=False)

        # Process the call for the current branch
        self.__invoke(processed_branch.current_block, processed_branch)

        completed_branch = False
        if processed_branch.current_block.next:
            # Move the branch forward
            processed_branch.step += 1
            processed_branch.current_block = processed_branch.current_block.next
            # Move on to the next branch
            self.__current_branch = (self.__current_branch + 1) % len(self.__branches)
        else:
            completed_branch = True
            # Remove the branch as it has been completed
            self.__branches.pop(self.__current_branch)
            # If the removed branch was the last, move on to the next branch
            # otherwise, the index will already be pointing to the next branch
            if (self.__current_branch == len(self.__branches)):
                self.__current_branch = 0
            # If there are no more branches, reset the pointer
            if (len(self.__branches) == 0):
                self.__current_branch = None

        return StepResult(processed_branch=processed_branch, completed_branch=completed_branch)
