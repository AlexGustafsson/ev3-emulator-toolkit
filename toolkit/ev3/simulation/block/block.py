from typing import TypedDict, Optional, Dict
from dataclasses import dataclass

@dataclass
class BlockVariableDefinition():
    type: str
    id: str
    name: str

@dataclass
class BlockField():
    name: str
    id: Optional[str]
    variable_type: Optional[str]
    value: str

@dataclass
class BlockShadow():
    type: str
    fields: Dict[str, BlockField]

@dataclass
class BlockValue():
    name: str
    shadow: BlockShadow

# TODO: Needs more test cases to verify implementation
@dataclass
class BlockMutation():
    expanded: int
    input_init: bool

@dataclass
class Block():
    # Location of the block
    x: Optional[int]
    # Location of the block
    y: Optional[int]
    # Block type, such as "variable_set"
    type: str
    fields: Dict[str, BlockField]
    values: Dict[str, BlockValue]
    # The next block to process
    next: Optional["Block"]
    disabled: bool
    # Statements such as HANDLER for event handlers
    statements: Dict[str, "Block"]
