import os
import sys
import numpy
import logging
from matplotlib import pyplot

# This Django logger is defined in settings/logsetup.py
logger = logging.getLogger("console")

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
    # This logger overwrites the Django logger and is used when the script is
    # called directly rather than imported by the Django management command.
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger.info("Running {0}".format(__file__))

    data = parse_author_year()
    logger.debug("\ndata: {0}".format(data))
