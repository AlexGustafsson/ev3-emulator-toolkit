import sys
import logging

from tools.uf2.uf2 import UF2
from tools.pxt.project import Project
from tools.ev3.simulation.simulator import Simulator

log = logging.getLogger(__name__)

def main() -> None:
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] [%(module)s] %(message)s')

    # Read the archive from the first parameter
    uf2 = UF2.read(sys.argv[1])
    project = Project(uf2)
    simulator = Simulator(project)

    simulator.start()
    simulator.run()

if __name__ == '__main__':
    main()
