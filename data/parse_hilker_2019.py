import os
import sys
import numpy
import logging
import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot
from urllib.parse import urlparse

from django.utils.text import slugify

# from .plotsettings import *

logger = logging.getLogger("console")

BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_GCS_Hilker2019/"


def parse_hilker_2019_orbits(fname="{0}orbits_table.txt".format(BASEDIR), debug=False):
    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/orbits_table.txt
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
    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/combined_table.txt
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    if debug:
        logger.debug("\nParsing Hilker+ (2019) combined table")

    names = [
        "Cluster", "RA", "DEC", "R_Sun", "R_GC",
        "Mass", "DM", "V", "V_err", "M/L_V", "M/L_V_err", "rc",
        "rh,l", "rh,m", "rt", "rho_c", "rho_h,m",
        "sig_c", "sig_h,m", "lg(Trh)", "MF", "F_REM",
        "sig0", "vesc", "etac", "etah",
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
    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/rv.dat
    # The following Table contains the velocity dispersion profiles of 139
    # Galactic globular clusters. The Table is based on the following papers:
    #   - Watkins et al. (2015), ApJ 803, 29
    #   - Baumgardt (2017), MNRAS 464, 2174
    #   - Kamann et al. (2018), MNRAS, 473, 5591
    #   - Baumgardt & Hilker (2018), MNRAS 478, 1520
    #   - Baumgardt, Hilker, Sollima & Bellini (2019), MNRAS 482, 5138

    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    if debug:
        logger.debug("\nParsing Hilker+ (2019) velocity dispersion profiles")

    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/veldis.html
    # does have a column NStar, but that column is not available for
    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/rv.dat
    names = [
        "Cluster", "radius", "velocity_dispersion",
        "velocity_dispersion_err_up", "velocity_dispersion_err_down",
        "type",
    ]
    dtype = [
        "S16", "float", "float", "float", "float", "S16"
    ]
    delimiter = [
        14, 7, 6, 6, 6, 6
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

    data = numpy.genfromtxt(fname, skip_header=0, delimiter=delimiter,
        dtype=dtype, names=names, autostrip=True)
    if debug:
        logger.debug("\nHere is the first entry:")
        for n in data.dtype.names:
            logger.debug("{0:<40s}{1}".format(n, data[0][n]))

        logger.debug("\ndelimiter.cumsum()\n{0}\n".format(numpy.array(delimiter).cumsum()))

        logger.debug("\nHere are the first five rows:")
        for i in range(5): logger.debug(data[i])

        logger.debug("\nHere are the colums Cluster"+
            "of the first five rows")
        logger.debug(data["Cluster"][0:5])

    return data


def scrape_individual_fits_from_baumgardt_website(logger,
        outdir="{0}figures/".format(BASEDIR), force_get_img=False):
    """ Retrieve the GAIA selection, Orbit over last 2 Gyr (xy and Rz plane),
        HST photometry, Mass function, and N-body fit gif/pdf images from the
        website of Holger Baumgardt. This function returns a dict /w GC name
        as keys, where the values are a (nested) dict with key: the url of the
        img src, and value: path to where the image is stored locally.

        The data ingestion script can later insert Auxiliary instances with
        Reference Baumgardt & Hilker (2018) b/c that seems to be the reference
        for the Nbody fits to the data? The AstroObject can be retrieved using
        the GC name, path = the local image, and url will be the img src."""

    base_url = "https://people.smp.uq.edu.au/HolgerBaumgardt/globular/fits/"
    clusterlist = "{0}clusterlist.html".format(base_url)

    r = requests.get(clusterlist)
    if r.status_code != 200:
        logger.error("ERROR: could not retrieve {0}".format(clusterlist))
        return
    soup = BeautifulSoup(r.content, "lxml")

    gcs = [( a.text, "{0}{1}".format(base_url, a["href"]) ) for a in soup.find_all("a")]
    Ngcs = len(gcs)
    logger.info("Found {0} globular clusters\n".format(Ngcs))

    # Get the nodata.gif in case we hit 404 at the individual GC pages later on
    nodata = "{0}nodata.gif".format(outdir)
    if not os.path.exists(nodata) and not os.path.isfile(nodata):
        logger.info("GET nodata.gif")
        nodata_url = "{0}phot/nodata.gif".format(base_url)
        r = requests.get(nodata_url, stream=True)
        if r.status_code != 200:
            logger.error("  ERROR: could not retrieve {0}".format(nodata_url))
            import sys; sys.exit(1)
        with open(nodata, "wb") as f:
            for chunk in r:  # reads the data in chunks of 128 bytes
                f.write(chunk)
        logger.info("Success GET nodata.gif\n")
    else:
        logger.info("File exists: {0}\n".format(nodata))

    figures = [
        "GAIA_selection", "Orbit_last_2Gyr_xy", "Orbit_last_2Gyr_Rz",
        "HST_photometry", "Mass_function", "Nbody_fit"
    ]
    data = dict()
    for i, gc in enumerate(gcs):
        gc_name, gc_url = gc
        data[gc_name] = dict()
        data[gc_name]["url"] = gc_url
        logger.info("\nGET {0}/{1}: {2} @ {3}".format(i+1, Ngcs, gc_name, gc_url))

        r = requests.get(gc_url)
        if r.status_code != 200:
            logger.error("  ERROR: could not retrieve {0}".format(gc_url))
            void = input("Press any key to continue")
            continue
        soup = BeautifulSoup(r.content, "lxml")

        for img, fig_name in zip(soup.find_all("img"), figures):
            img_src = "{0}{1}".format(base_url, img["src"])
            logger.info("    {0} --> {1}".format(fig_name, img_src))

            path = urlparse(img_src).path
            ext = os.path.splitext(path)[1]
            fname = "{0}{1}_{2}{3}".format(outdir, slugify(gc_name), fig_name, ext)
            data[gc_name]["img_src"] = fname
            if os.path.exists(fname) and os.path.isfile(fname) and not force_get_img:
                logger.info("    already have {0}".format(fname))
                continue

            logger.info("    saving as {0}".format(fname))
            r = requests.get(img_src, stream=True)
            if r.status_code != 200:
                logger.warning("  WARNING: could not retrieve {0}. Set to nodata.gif".format(img_src))
                os.system("cp {0} {1}".format(nodata, fname))
            with open(fname, "wb") as f:
                for chunk in r:  # reads the data in chunks of 128 bytes
                    f.write(chunk)

    return data


def parse_individual_rvs_of_stars_in_field_of_clusters(logger, debug=True,
        fname="{0}appendix_combined_table.txt".format(BASEDIR)):
    """ Data retrieved 20191017 from
    https://people.smp.uq.edu.au/HolgerBaumgardt/globular/appendix/appendix.html,
    link at bottom 'Click here for an ASCII file with the combined radial velocity data of all clusters.'
    --> https://people.smp.uq.edu.au/HolgerBaumgardt/globular/appendix/combined_table.txt

    'The following table contains the individual stellar radial velocities that
    we derived from ESO proposals prior to 2014. The data files also contain the
    Gaia DR2, APOGEE DR14, Keck/DEIMOS, Keck/HIRES and Keck/NIRSPEC radial
    velocities which are not included in Appendix D of the MNRAS paper. At the
    moment the data files contain about 1/3 of all radial velocities. The
    inclusion of the remaining data is underway... '

    This function parses the combined_table.txt file.
    """

    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    if debug:
        logger.debug("\nParsing Hilker+ (2019) individual radial velocity data")

    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/veldis.html
    # does have a column NStar, but that column is not available for
    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/rv.dat
    names = [
        "Cluster", "2MASS_ID", "RA", "DEC", "RV", "E_RV",
        "DCEN", "J_mag", "E_J_mag", "K_mag", "E_K_mag", "P_Mem", "NRV", "P_Single",
    ]
    dtype = [
        "U16", "U18", "float", "float", "float", "float",
        "float", "float", "float", "float", "float", "float", "int", "float"
    ]
    delimiter = [
        9, 18, 13, 13, 10, 10,
        9, 6, 6, 8, 6, 10, 3, 9
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
            logger.debug("{0:<40s}{1}".format(n, data[0][n]))
        logger.debug("\nHere is the 129th entry:")
        for n in data.dtype.names:
            logger.debug("{0:<40s}{1}".format(n, data[129][n]))

        logger.debug("\ndelimiter.cumsum()\n{0}\n".format(numpy.array(delimiter).cumsum()))

        logger.debug("\nHere are the first 50 rows:")
        for i in range(50): logger.debug(data[i])

    return data


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger.info("Running {0}".format(__file__))

    individual_rvs = parse_individual_rvs_of_stars_in_field_of_clusters(logger)
    import sys; sys.exit(0)

    hilker_orbits = parse_hilker_2019_orbits(debug=True)

    hilker_combined = parse_hilker_2019_combined(debug=True)
    # It seems Ter 2 has three nan values. So here we check which and why.
    ter2, = numpy.where(hilker_combined["Cluster"] == b"Ter 2")
    for n in hilker_combined.dtype.names:
        logger.debug("{0:<20s}{1}".format(n, hilker_combined[ter2][0][n]))

    hilker_radial_velocities = parse_hilker_2019_radial_velocities(debug=True)

    gc_fits = scrape_individual_fits_from_baumgardt_website(logger)
