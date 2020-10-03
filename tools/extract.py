import os
import sys
import json
import logging
from pathlib import Path

from tools.uf2.uf2 import UF2
from tools.pxt.project import Project

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] [%(module)s] %(message)s')


def main() -> None:
    # Read the archive from the first parameter
    uf2 = UF2.read(sys.argv[1])
    logging.debug("Read UF2 file with {} blocks".format(len(uf2.blocks)))

    project = Project(uf2)
    logging.info("Found project '{}'".format(project.name))

    # Save meta for the source
    if project.meta is not None:
        path = "./files/{}/meta.json".format(project.name)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            json.dump(project.meta, file, indent=2)
        logging.info("Successfully extracted meta data to {}".format(path))

    # Save meta for the source
    if project.source_meta is not None:
        path = "./files/{}/source-meta.json".format(project.name)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            json.dump(project.source_meta, file, indent=2)
        logging.info("Successfully extracted source meta data to {}".format(path))

    # Save the source itself
    if project.source is not None:
        path = "./files/{}/source.json".format(project.name)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            json.dump(project.source, file, indent=2)
        logging.info("Successfully extracted source to {}".format(path))

    # Save all source files
    for filename, content in project.files:
        path = os.path.join("./files/{}/source/".format(project.name), filename)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
           file.write(content)
        logging.info("Successfully extracted source file {} to {}".format(filename, path))

    # Save all UF2 files
    files = uf2.extract_files()
    for filename, content in files.items():
        path = os.path.join("./files/{}/root/".format(project.name), filename)
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as file:
           file.write(content)
        logging.info("Successfully extracted file {} to {}".format(filename, path))

if __name__ == '__main__':
    main()
