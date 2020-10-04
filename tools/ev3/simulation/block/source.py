from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from typing import Dict, Iterator, List

from tools.ev3.simulation.block.block import Block, BlockField, BlockShadow, BlockValue, BlockVariableDefinition

class BlockSource:
    """Abstraction for a block source, such as the main.block XML file."""
    def __init__(self, source: str) -> None:
        self.__variables: Dict[str, BlockVariableDefinition] = {}
        self.__blocks: List[Block] = []

        ElementTree.register_namespace("", "http://www.w3.org/1999/xhtml")
        root = ElementTree.fromstring(source)
        self.__parse(root)

    def __parse_variables(self, element: Element) -> Dict[str, BlockVariableDefinition]:
        variables: Dict[str, BlockVariableDefinition] = {}
        for variable_element in element:
            variable = BlockVariableDefinition(
                type=variable_element.attrib["type"],
                id=variable_element.attrib["id"],
                name=variable_element.text
            )
            variables[variable.id] = variable
        return variables

    def __parse_block_field(self, element: Element) -> BlockField:
        field = BlockField(
            name=element.attrib["name"],
            id=element.attrib["id"] if "id" in element.attrib else None,
            variable_type=element.attrib["variabletype"] if "variabletype" in element.attrib else None,
            value=element.text,
        )
        return field

    def __parse_block(self, element: Element) -> Block:
        statements: Dict[str, Block] = {}
        fields = {}
        values = {}
        next = None
        for child in element:
            if self.__clean_tag_name(child) == "statement":
                statements[child.attrib["name"]] = self.__parse_block(child[0])
            elif self.__clean_tag_name(child) == "field":
                field = self.__parse_block_field(child)
                fields[field.name] = field
            elif self.__clean_tag_name(child) == "value":
                block_fields = {}
                for child2 in child[0]:
                    if self.__clean_tag_name(child2) == "field":
                        field = self.__parse_block_field(child2)
                        block_fields[field.name] = field
                block_shadow = BlockShadow(
                    type=child[0].attrib["type"],
                    fields=block_fields
                )
                value = BlockValue(
                    name=child.attrib["name"],
                    shadow=block_shadow
                )
                values[value.name] = value
            elif self.__clean_tag_name(child) == "next":
                next = self.__parse_block(child[0])
        return Block(
            statements=statements,
            fields=fields,
            values=values,
            next=next,
            type=element.attrib["type"],
            x=element.attrib["x"] if "x" in element.attrib else None,
            y=element.attrib["y"] if "y" in element.attrib else None,
            disabled=element.attrib["disabled"] if "disabled" in element.attrib else False
        )

    def __clean_tag_name(self, element: Element) -> str:
        if "{http://www.w3.org/1999/xhtml}" in element.tag:
            return element.tag[len("{http://www.w3.org/1999/xhtml}"):]
        return element.tag

    def __parse(self, root: Element) -> None:
        for element in root:
            if self.__clean_tag_name(element) == "variables":
                self.__variables = self.__parse_variables(element)
            elif self.__clean_tag_name(element) == "block":
                self.__blocks.append(self.__parse_block(element))

    @property
    def blocks(self) -> List[Block]:
        return self.__blocks

    @property
    def variables(self) -> Dict[str, BlockVariableDefinition]:
        return self.__variables

    def blocks_by_type(self, type: str) -> Iterator[Block]:
        return [block for block in self.__blocks if block.type == type]
