import os
import numpy
import matplotlib
from matplotlib import pyplot

# from .plotsettings import *


def parse_orbits(fname="MW_GCS_Hilker2019/orbits_table.txt", debug=True):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        print("ERROR: file not found: {0}".format(fname))
        return

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
        print("\nnames:     {}\ndtype:     {}\ndelimiter: {}\n".format(
        len(names), len(dtype), len(delimiter) ))

        print("\n(name, dtype, delimiter)")
        for i in range(len(names)):
            print(names[i], dtype[i], delimiter[i])
        print("")

    data = numpy.genfromtxt(fname, skip_header=2, delimiter=delimiter,
        dtype=dtype, names=names, autostrip=True)
    if debug:
        print("\nHere is the first entry:")
        for n in data.dtype.names:
            print("{0:<20s}{1}".format(n, data[0][n]))

        print("\nHere are the first five rows:")
        for i in range(5): print(data[i])

        print("\nHere are the colums Cluster, mualpha, mualpha_err, RPERI, RPERI_err")
        print(data["Cluster"])
        print(data["mualpha"])
        print(data["mualpha_err"])
        print(data["RPERI"])
        print(data["RPERI_err"])

    return data


if __name__ == "__main__":
    orbit_data = parse_orbits()
