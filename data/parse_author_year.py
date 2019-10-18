import os
import sys
import numpy
import logging
from matplotlib import pyplot


BASEDIR = "/".join(__file__.split("/")[:-1]) + "/folder/"


def parse_author_year(fname="{0}my_database.csv".format(BASEDIR)):
    # with open(fname) as f:
    #     f.readlines()

    # e.g. GCName, R_Sun
    data = [
        ["Terzan 5", 6.900],
    ]

    return data


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger = logging.getLogger(__file__)
    logger.info("Running {0}".format(__file__))

    data = parse_author_year()
    logger.debug("\ndata: {0}".format(data))
