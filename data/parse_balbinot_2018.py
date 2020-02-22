import os
import sys
import numpy
import logging
from matplotlib import pyplot


BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_GCS_Balbinot2018/"


def parse_balbinot_2018(logger, fname="{0}latex_table_semi_cleaned.txt".format(BASEDIR)):
    with open(fname) as f:
        raw_data = f.readlines()

    logger.debug("Found {0} entries".format(len(raw_data)))

    return []


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger = logging.getLogger(__file__)
    logger.info("Running {0}".format(__file__))

    data = parse_balbinot_2018(logger)
    logger.debug("\ndata: {0}".format(data))
