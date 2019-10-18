import os
import sys
import numpy
import logging
from matplotlib import pyplot
from astroquery.vizier import Vizier
Vizier.ROW_LIMIT = -1


def parse_trager_1995_gc():
    return Vizier.get_catalogs("J/AJ/109/218/gc")[0]


def parse_trager_1995_tables():
    return Vizier.get_catalogs("J/AJ/109/218/tables")[0]


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger = logging.getLogger(__file__)
    logger.info("Running {0}".format(__file__))

    gc = parse_trager_1995_gc()
    logger.debug("\ngc has {0} entries".format(len(gc)))
    logger.debug("keys: {0}".format(gc.keys()))
    tables = parse_trager_1995_tables()
    logger.debug("\ntables has {0} entries".format(len(tables)))
    logger.debug("keys: {0}".format(tables.keys()))
