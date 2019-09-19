import os
import sys
import numpy
import logging
from matplotlib import pyplot

# from .plotsettings import *

logger = logging.getLogger("console")

BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_GCS_Hilker2019/"


def parse_hilker_2019_orbits(fname="{0}orbits_table.txt".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    if debug:
        logger.debug("\nParsing Hilker+ (2019) orbits table")

    names = [
        "Cluster", "RA", "DEC", "l", "b",
        "Rsun", "ERsun", "R_GC", "<RV>", "ERV",
        "mualpha", "mualpha_err", "mu_delta", "mu_delta_err", "rhopmrade",
        "X", "DX", "Y", "DY", "Z",
        "DZ", "U", "DU", "V", "DV",
        "W", "DW", "RPERI", "RPERI_err", "RAP",
        "RAP_err"
    ]
    dtype = [
        "S16", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float"
    ]
    delimiter = [
        16, 10, 11, 8, 8,
        8, 8, 8, 8, 8,
        8, 7, 8, 8, 8,
        5, 8, 8, 8, 6,
        8, 8, 10, 8, 8,
        10, 8, 8, 8, 8,
        8
    ]

    if debug:
        logger.debug("\nnames:     {}\ndtype:     {}\ndelimiter: {}\n".format(
        len(names), len(dtype), len(delimiter) ))

        logger.debug("-"*45)
        logger.debug("{0:<15s}{1:<15s}{2:<15s}".format("name", "dtype", "delimiter"))
        logger.debug("-"*45)
        for i in range(len(names)):
            logger.debug("{0:<15s}{1:<15s}{2:<15d}".format(names[i], dtype[i], delimiter[i]))
        logger.debug("-"*45 + "\n")

    data = numpy.genfromtxt(fname, skip_header=2, delimiter=delimiter,
        dtype=dtype, names=names, autostrip=True)
    if debug:
        logger.debug("\nHere is the first entry:")
        for n in data.dtype.names:
            logger.debug("{0:<20s}{1}".format(n, data[0][n]))

        logger.debug("\nHere are the first five rows:")
        for i in range(5): logger.debug(data[i])

        logger.debug("\nHere are the colums Cluster, mualpha, "+
            "mualpha_err, RPERI, RPERI_err of the first five rows")
        logger.debug(data["Cluster"][0:5])
        logger.debug(data["mualpha"][0:5])
        logger.debug(data["mualpha_err"][0:5])
        logger.debug(data["RPERI"][0:5])
        logger.debug(data["RPERI_err"][0:5])

    return data


def parse_hilker_2019_combined(fname="{0}combined_table.txt".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    if debug:
        logger.debug("\nParsing Hilker+ (2019) combined table")

    # TODO: something iffy is going on b/c we have two more columns in each
    # row than the header indicates ...
    names = [
        "Cluster", "RA", "DEC", "R_Sun", "R_GC",
        "Mass", "DM", "V", "M/L_V", "rc",
        "rh,l", "rh,m", "rt", "rho_c", "rho_h,m",
        "sig_c", "sig_h,m", "lg(Trh)", "MF", "F_REM",
        "sig0", "vesc", "etac", "etah", "something",
        "something2",
    ]
    dtype = [
        "S16", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float", "float", "float", "float", "float",
        "float",
    ]
    delimiter = [
        14, 10, 11, 8, 9,
        12, 12, 6, 6, 7,
        8, 7, 8, 9, 10,
        7, 8, 8, 10, 6,
        8, 8, 6, 8, 6,
        7,
    ]

    if debug and False:
        logger.debug("\nnames:     {}\ndtype:     {}\ndelimiter: {}\n".format(
        len(names), len(dtype), len(delimiter) ))

        logger.debug("-"*45)
        logger.debug("{0:<15s}{1:<15s}{2:<15s}".format("name", "dtype", "delimiter"))
        logger.debug("-"*45)
        for i in range(len(names)):
            logger.debug("{0:<15s}{1:<15s}{2:<15d}".format(names[i], dtype[i], delimiter[i]))
        logger.debug("-"*45 + "\n")

    data = numpy.genfromtxt(fname, skip_header=2, delimiter=delimiter,
        dtype=dtype, names=names, autostrip=True)
    if debug:
        logger.debug("\nHere is the first entry:")
        for n in data.dtype.names:
            logger.debug("{0:<20s}{1}".format(n, data[0][n]))

        logger.debug("\ndelimiter.cumsum()\n{0}\n".format(numpy.array(delimiter).cumsum()))

        logger.debug("\nHere are the first five rows:")
        for i in range(5): logger.debug(data[i])

        logger.debug("\nHere are the colums Cluster"+
            "of the first five rows")
        logger.debug(data["Cluster"][0:5])

    return data



def parse_hilker_2019_radial_velocities(fname="{0}rv.dat".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger.info("Running {0}".format(__file__))

    # hilker_orbits = parse_hilker_2019_orbits(debug=True)

    hilker_combined = parse_hilker_2019_combined(debug=True)
    # It seems Ter 2 has three nan values. So here we check which and why.
    ter2, = numpy.where(hilker_combined["Cluster"] == b"Ter 2")
    for n in hilker_combined.dtype.names:
        logger.debug("{0:<20s}{1}".format(n, hilker_combined[ter2][0][n]))

    # hilker_radial_velocities = parse_hilker_2019_radial_velocities(debug=True)
