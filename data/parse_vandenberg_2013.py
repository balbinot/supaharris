import os
import numpy
import logging

logger = logging.getLogger("console")
logger.logLevel = logging.DEBUG

BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_GCS_VandenBerg2013/"


def read_vandenberg2013_data(fname="{0}table2.txt".format(BASEDIR)):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        print("ERROR: file not found: {0}".format(fname))
        return

    dtype = [
        "int", "S10", "float", "float", "float", "S1", "S5", "S12",
        "float", "float", "float", "float", "float"
    ]
    names = [
        "NGC", "Name", "[Fe/H]", "Age", "fAge", "Method", "Fig", "Range",
        "HBType", "R_GC", "M_Vt", "v_e0", "log10sigma0"
    ]
    data = numpy.genfromtxt(fname, delimiter=",", dtype=dtype, names=names)

    dtype = numpy.dtype(data.dtype.descr + [("sigma0", "float")])
    data2 = numpy.empty(data.shape, dtype=dtype)
    for name in data.dtype.names:
        data2[name] = data[name]
    data2["sigma0"] = 10**data["log10sigma0"]
    return data2


def print_vandenberg2013_data(data, first_five_rows=True):
    width = 130

    print("\n{0}".format("-"*width))
    print("{0:<6s}{1:^7}{2:^8s}{3:^8s}{4:^8s}{5:^8s}{6:^7s}{7:^16s}".format(
        "NGC", "Name", "[Fe/H]", "Age", "fAge", "Method", "Fig", "Range"), end="")
    print("{0:>8s}{1:>8s}{2:>8s}{3:>8s}{4:>15s}{5:>15s}".format(
        "HBType", "R_GC", "M_V", "v_e,0", "log(sigma0)", "sigma0"))
    print("{0}".format("-"*width))
    for i, row in enumerate(data):
        print("{0:<6s}{1:^7s}{2:^8.2f}{3:^8.2f}{4:^8.2f}{5:^8s}{6:^7s}{7:^16s}".format(
            str(row[0]), row[1].decode("ascii"), row[2], row[3],
            row[4], row[5].decode("ascii"), row[6].decode("ascii"),
            row[7].decode("ascii")), end="")
        print("{0: 8.1f}{1: 8.1f}{2: 8.1f}{3: 8.1f}{4: 15.3f}{5: 15.1f}".format(
            row[8], row[9], row[10], row[11], row[12], row[13]))
        if first_five_rows and i > 3: break
    print("{0}\n".format("-"*width))


def plot_vandenberg2013_figure33(data, ax=None):
    if not ax:
        fig, ax = pyplot.subplots(figsize=(12, 9))

    label = r"\begin{{tabular}}{{p{{6cm}}l}}MW: VandenBerg (2013); & Ngc = {0}\end{{tabular}}"\
        .format(len(data))
    ax.errorbar(data["FeH"], data["Age"], xerr=0.15, yerr=data["fAge"],
        marker="o", ls="", c="k", ms=4, elinewidth=2, capsize=4, label=label)

    ax.set_xticks(numpy.arange(-2.5, 0.5, 0.5))
    ax.set_xticks(numpy.arange(-2.5, 0.1, 0.1), minor=True)
    ax.set_yticks(numpy.arange(10, 15, 1))
    ax.set_yticks(numpy.arange(10, 14.2, 0.2), minor=True)
    pyplot.xlim(-2.6, 0)
    pyplot.ylim(9.8, 14)
    pyplot.xlabel("[Fe/H]")
    pyplot.ylabel("Age (Gyr)")
    if not ax:
        pyplot.show()

    pyplot.savefig("vandenberg_2013_fig33.pdf")


if __name__ == "__main__":
    from plotsettings import *
    from matplotlib import pyplot

    pyplot.switch_backend("agg")

    data = read_vandenberg2013_data()
    print_vandenberg2013_data(data, first_five_rows=False)
    plot_vandenberg2013_figure33(data)
