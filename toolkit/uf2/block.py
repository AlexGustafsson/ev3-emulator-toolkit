import struct
from typing import Tuple
from struct import Struct

NOT_MAIN_FLASH = 0x00000001
FILE_CONTAINER = 0x00001000
FAMILY_ID_PRESENT = 0x00002000
MD5_CHECKSUM_PRESENT = 0x00004000
EXTENSION_TAGS_PRESENT = 0x00008000

MAGIC_NUMBER_0 = struct.pack('<L', 0x0A324655)
MAGIC_NUMBER_1 = struct.pack('<L', 0x9E5D5157)
MAGIC_NUMBER_END = struct.pack('<L', 0x0AB16F30)

# struct UF2_Block {
#     // 32 byte header
#     uint32_t magicStart0;
#     uint32_t magicStart1;
#     uint32_t flags;
#     uint32_t targetAddr;
#     uint32_t payloadSize;
#     uint32_t blockNo;
#     uint32_t numBlocks;
#     uint32_t fileSize; // or familyID;
#     uint8_t data[476];
#     uint32_t magicEnd;
# } UF2_Block;
block_struct = Struct('<4s4s6L476s4s')
checksum_struct = Struct('<2L4s')

class Block():
    def __init__(self, bytes: bytes) -> None:
        """Create a block from the given bytes."""
        self.__magic_start_0, self.__magic_start_1, self.__flags, self.__target_address, self.__payload_size, self.__block_number, self.__number_of_blocks, self.__file_size_or_family_id, self.__data, self.__magic_end = block_struct.unpack(bytes)

    @property
    def magic_start_0(self) -> bytes:
        """First magic number, 0x0A324655 ("UF2\\n")."""
        return self.__magic_start_0

    @property
    def magic_start_1(self) -> bytes:
        """Second magic number, 0x9E5D5157."""
        return self.__magic_start_1

    @property
    def magic_start(self) -> bytes:
        """Magic bytes."""
        return self.__magic_start_0 + self.__magic_start_1

    @property
    def flags(self) -> int:
        """Flags."""
        return self.__flags

    @property
    def target_address(self) -> int:
        """Address in flash where the data should be written."""
        return self.__target_address

    @property
    def payload_size(self) -> int:
        """Number of bytes used in data (often 256)."""
        return self.__payload_size

    @property
    def block_number(self) -> int:
        """Sequential block number; starts at 0."""
        return self.__block_number

    @property
    def number_of_blocks(self) -> int:
        """Total number of blocks in file."""
        return self.__number_of_blocks

    @property
    def file_size(self) -> int:
        """File size or board family ID or zero."""
        return self.__file_size_or_family_id

    @property
    def family_id(self) -> int:
        """File size or board family ID or zero."""
        return self.__file_size_or_family_id

    @property
    def data(self) -> bytes:
        """Data, excluding padding and the optional checksum."""
        return self.__data[0:self.__payload_size]

    @property
    def magic_end(self) -> bytes:
        """Final magic number, 0x0AB16F30."""
        return self.__magic_end

    @property
    def checksum(self) -> Tuple[int, int, bytes]:
        """The optionally specified checksum."""
        if not self.is_md5_checksum_present:
            return None

        return checksum_struct.unpack(self.__data[-24::])

    @property
    def filename(self) -> str:
        """The filename if specified."""
        if not self.is_file_container:
            return None

        string_termination = self.__data.index(b'\x00', self.__payload_size)
        return self.__data[self.__payload_size:string_termination].decode()

    @property
    def is_not_main_flash(self) -> bool:
        """Whether or not the block is meant for the main flash."""
        return self.__flags & NOT_MAIN_FLASH > 0

    @property
    def is_file_container(self) -> bool:
        """Whether or not the block is part of a file container."""
        return self.__flags & FILE_CONTAINER > 0

    @property
    def is_family_id_present(self) -> bool:
        """Whether or not a family id is present."""
        return self.__flags & FAMILY_ID_PRESENT > 0

    @property
    def is_md5_checksum_present(self) -> bool:
        """Whether or not a md5 checksum is present."""
        return self.__flags & MD5_CHECKSUM_PRESENT > 0

    @property
    def is_extension_tags_present(self) -> bool:
        """Whether or not extension tags are present."""
        return self.__flags & EXTENSION_TAGS_PRESENT > 0

    def pack(self) -> bytes:
        """Pack the block into bytes."""
        return block_struct.pack(self.__magic_start_0, self.__magic_start_1, self.__flags, self.__target_address, self.__payload_size, self.__block_number, self.__number_of_blocks, self.__file_size_or_family_id, self.__data, self.__magic_end)

    def validate(self) -> None:
        """Validate the block."""
        if not self.__magic_start_0 == MAGIC_NUMBER_0:
            raise Exception("Got bad magic number 1. Expected {}, got {}".format(MAGIC_NUMBER_0, self.__magic_start_0))
        if not self.__magic_start_1 == MAGIC_NUMBER_1:
            raise Exception("Got bad magic number 2. Expected {}, got {}".format(MAGIC_NUMBER_1, self.__magic_start_1))
        if not self.__magic_end == MAGIC_NUMBER_END:
            raise Exception("Got bad end magic number. Expected {}, got {}".format(MAGIC_NUMBER_END, self.__magic_end))
