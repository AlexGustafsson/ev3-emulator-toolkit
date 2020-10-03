import os
import sys
import json
import lzma
import struct
import logging
from typing import Tuple, Iterator
from pathlib import Path
from lzma import LZMAError, LZMADecompressor

from uf2.uf2 import UF2

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] [%(module)s] %(message)s')

def find_meta_blocks(payload: bytes) -> Iterator[int]:
    """Loop through the data to find any matching block start."""
    # The magic number of the meta data hidden within the binary data
    # payload of some block (the ELF block in this case)
    magic = bytes([0x41, 0x14, 0x0E, 0x2F, 0xB8, 0x2F, 0xA2, 0xBB])
    for i in range(0, len(payload), 16):
        current_magic = payload[i:i + 8]

        # Compare the magic number to the first 8 bytes
        if current_magic == magic:
            yield i

def extract_header(payload: bytes, meta_block_start: int) -> Tuple[int, int]:
    """Extract the lengths of the fields."""
    header = payload[meta_block_start + 8:meta_block_start + 16]
    meta_length = struct.unpack("<H", bytes(header[0:2]))[0]
    text_length = struct.unpack("<I", bytes(header[2:6]))[0]
    return (meta_length, text_length)

def extract_meta(payload: bytes, meta_block_start: int, meta_length: int, text_length: int) -> Tuple[object, bytes]:
    """Extract the meta fields."""
    # Default values for the meta
    meta = {
        "compression": None,
        "headerSize": 0,
        "textSize": 0,
        "name": "",
        "eURL": "https://makecode.mindstorms.com/",
        "eVER": "1.2.30",
        "pxtTarget": "ev3"
    }

    compressed_text = None

    meta_start = meta_block_start + 16
    meta_end = meta_start + meta_length

    text_start = meta_end
    text_end = text_start + text_length

    meta = json.loads(payload[meta_start:meta_end])
    compressed_text = payload[text_start:text_end]

    return (meta, compressed_text)


def lzma_decompress(compressed: bytes) -> bytes:
    """Decompress LZMA data."""
    # Log the printf-friendly hex representation of the bytes to decompress
    hex = compressed.hex()
    hex = "\\x" + "\\x".join([hex[i:i+2] for i in range(0, len(hex), 2)])
    logging.debug("Attempting LZMA decompression of bytes: {}".format(hex))

    properties, dictionary_size, uncompressed_size = struct.unpack("<BIQ", compressed[:13])
    if properties > (4 * 5 + 4) * 9 + 8:
        logging.warning("There seems to be an issue in the LZMA header")

    position_bits = properties // (9 * 5)
    literal_position_bits = (properties - position_bits * 9 * 5) // 9
    literal_context_bits = (properties - position_bits * 9 * 5) - literal_position_bits * 9

    logging.debug("LZMA dictionary_size={}".format(dictionary_size))
    logging.debug("LZMA uncompressed_size={}".format(uncompressed_size))
    logging.debug("LZMA literal_context_bits={}".format(literal_context_bits))
    logging.debug("LZMA literal_position_bits={}".format(literal_position_bits))
    logging.debug("LZMA position_bits={}".format(position_bits))

    if literal_context_bits + literal_position_bits > 4:
        logging.warning("literal_context_bits + litereal_position_bits > 4 which may indicate LZMA header issues")

    # lzma-js as used by PXT has a bug where the EOF marker is written incorrectly
    # disable it.
    # See: https://github.com/LZMA-JS/LZMA-JS/issues/44
    # See: https://github.com/LZMA-JS/LZMA-JS/issues/54
    # return lzma.decompress(compressed[:-6], lzma.FORMAT_ALONE)
    decompressor = LZMADecompressor(lzma.FORMAT_ALONE, None, None)
    return decompressor.decompress(compressed[:-6])


def extract_sources(uf2: UF2) -> Iterator[Tuple[object, object, object]]:
    """
    Extract MakeCode sources from the archive.

    Based off of the pxt source code from https://github.com/microsoft/pxt,
    pxt/cpp.ts@extractSourceFromBin.
    """

    # All bytes in the correct order
    payload = uf2.extract_bytes()

    for meta_block_start in find_meta_blocks(payload):
        logging.debug("Found meta block at byte offset {}".format(meta_block_start))

        meta_length, text_length = extract_header(payload, meta_block_start)
        logging.debug("Meta length is {}".format(meta_length))
        logging.debug("Text length is {}".format(text_length))

        if meta_block_start + 16 + meta_length + text_length > len(payload):
            logging.debug("The meta size was too large, skipping")
            continue

        try:
            meta, compressed_text = extract_meta(payload, meta_block_start, meta_length, text_length)
        except ValueError:
            logging.warning("Unable to parse meta from JSON", exc_info=True)
            yield (None, None, None)
            continue

        # As per MakeCode, the only officially supported compression algorithm
        # is LZMA
        if not meta["compression"] == "LZMA":
            logging.warning("Unsupported compression algorithm: {}".format(meta["compression"]))
            yield (meta, None, None)
            continue

        try:
            text = lzma_decompress(compressed_text)

            source_length = meta["headerSize"] or meta["metaSize"] or 0
            source_meta = json.loads(text[0:source_length])
            source = json.loads(text[source_length:])
            yield (meta, source_meta, source)
        except LZMAError:
            logging.warning("Unable to decompress source", exc_info=True)
            yield (meta, None, None)


def main() -> None:
    # Read the archive from the first parameter
    uf2 = UF2.read(sys.argv[1])
    logging.debug("Read UF2 file with {} blocks".format(len(uf2.blocks)))

    meta, source_meta, source = next(extract_sources(uf2))
    project_name = "Untitled" if meta is None else meta["name"]
    logging.info("Found project '{}'".format(project_name))

    # Save meta for the source
    if meta is not None:
        path = "./files/{}/meta.json".format(project_name)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            json.dump(meta, file, indent=2)
        logging.info("Successfully extracted meta data to {}".format(path))

    # Save meta for the source
    if source_meta is not None:
        path = "./files/{}/source-meta.json".format(project_name)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            json.dump(source_meta, file, indent=2)
        logging.info("Successfully extracted source meta data to {}".format(path))

    # Save the source itself
    if source is not None:
        path = "./files/{}/source.json".format(project_name)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            json.dump(source, file, indent=2)
        logging.info("Successfully extracted source to {}".format(path))

    # Save all files
    files = uf2.extract_files()
    for filename, content in files.items():
        path = os.path.join("./files/{}/root/".format(project_name), filename)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as file:
           file.write(content)
        logging.info("Successfully extracted file {} to {}".format(filename, path))

if __name__ == '__main__':
    main()
