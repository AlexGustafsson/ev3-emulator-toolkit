import os
from typing import List

from uf2.block import Block

BLOCK_SIZE = 512

class UF2():
    def __init__(self, blocks: List[Block]) -> None:
        """Create a UF2 file from blocks."""
        self.__blocks = blocks

    @property
    def blocks(self) -> List[Block]:
        """All available blocks."""
        return self.__blocks

    def extract_binary(self) -> bytes:
        data: bytes = bytes()
        for block in self.__blocks:
            data += block.data[0:block.payload_size]
        return data

    # TODO: Unfinished
    def extract_files(self) -> List[str]:
        """Files in the archive."""
        files: Dict[str, bytes] = {}

        # validate UF2 magic numbers
        # make sure that targetAddr < fileSize and that fileSize isn't out of reasonable range
        # write 0x00 at data[475] to ensure NUL termination of file name
        # read file name from &data[payloadSize]; perform any mapping on the file name
        # create a directory where the file is to be written if doesn't exists
        # open the file for writing
        # truncate the file to fileSize
        # seek targetAddr
        # write the payload (ie., data[0 ... payloadSize - 1])
        # close the file

        for block in self.__blocks:
            if not block.is_file_container:
                continue

            if block.filename is None:
                raise Exception("Got bad filename")

            if block.filename not in files:
                files[block.filename] = bytearray(block.file_size)

            files[block.filename] = files[block.filename][0:block.target_address] + block.data + files[block.filename][block.target_address + block.payload_size:]

        return files


    @staticmethod
    def read(path: str) -> "UF2":
        """Read a UF2 file from a path."""
        file_size = os.path.getsize(path)
        if file_size % BLOCK_SIZE > 0:
            raise Exception("Got a bad block size, the file may be corrupt")

        blocks: List[Block] = []
        with open(path, "rb") as file:
            while True:
                raw = file.read(BLOCK_SIZE)
                if not raw:
                    break

                block = Block(raw)
                blocks.append(block)

        # Sort by block number
        blocks.sort(key=lambda block: block.block_number)

        # Validate blocks
        for block in blocks:
            block.validate()

        return UF2(blocks)
