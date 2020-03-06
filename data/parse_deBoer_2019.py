import os
import sys
import glob
import numpy
import logging
from matplotlib import pyplot


BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_GCS_deBoer2019/"


def fix_gc_names(name):
    if "/supaharris" not in sys.path:  # to allow import of utils
        sys.path.append("/supaharris")
    from utils import convert_gc_names_from_sh_to_any
    return convert_gc_names_from_sh_to_any(name, reverse=True)  # from deBoer to SH


def parse_deBoer_2019_fits(logger, fname="{0}GC_numdens_fit_pars_all_comb".format(BASEDIR)):
    # "https://github.com/tdboer/GC_profiles/tree/f31e147c1ac2de11146d421f261cc620340ae9a9"

    if not os.path.exists(fname) or not os.path.isfile(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    # b/c explicit is better than implicit, aye?
    names = [
        "id", "W_lime", "e_W_lime", "g_lime", "e_g_lime", "rt_lime", "e_rt_lime",
        "M_lime", "e_M_lime", "W_pe", "e_W_pe", "eta_pe", "e_eta_pe", "log1minB_pe",
        "e_log1minB_pe", "rt_pe", "e_rt_pe", "M_pe", "e_M_pe", "W_king", "e_W_king",
        "rt_king", "e_rt_king", "M_king", "e_M_king", "W_wil", "e_W_wil", "rt_wil",
        "e_rt_wil", "M_wil", "e_M_wil", "log_fpe", "e_log_fpe", "chi2_king", "chi2red_king",
        "chi2_wil", "chi2red_wil", "chi2_lime", "chi2red_lime", "chi2_pe", "chi2red_pe",
        "kingtrunc", "kinghalf", "wiltrunc", "wilhalf", "limehalf", "e_limehalf", "pehalf",
        "e_pehalf", "pecore", "e_pecore", "r_tie", "BGlev", "min_mass", "max_mass",
    ]
    dtype = ["U12"] + ["f8" for i in names[1:]]

    # or use names=True to read 'm from file ... :-)
    data = numpy.genfromtxt(fname, names=names, dtype=dtype)

    for i in range(data.shape[0]):  # for consistency /w SupaHarris AstroObject names
        data["id"][i] = fix_gc_names(data["id"][i])

    return data


def parse_deBoer_2019_member_stars(logger, dirname="{0}member_stars/".format(BASEDIR)):
    if not os.path.exists(dirname) or not os.path.isdir(dirname):
        logger.error("ERROR: dir not found: {0}".format(dirname))
        return

    files = glob.glob(dirname+"*")
    names = [
        "ra", "dec", "xi_gc", "xn_gc", "ellrad_gc",
        "pmra", "pmra_error", "pmdec", "pmdec_error",
        "parallax", "parallax_error",
        "phot_g_mean_mag", "phot_g_mean_mag_error",
        "phot_bp_mean_mag", "phot_bp_mean_mag_error",
        "phot_rp_mean_mag", "phot_rp_mean_mag_error",
        "phot_bp_rp_excess_factor", "Ag", "Abp", "Arp",
        "pmra_pmdec_corr", "source_id", "prob"
    ]

    data = dict()
    for fname in files:
        name = fix_gc_names(
            fname.split("member_stars/")[-1].replace(
                "_gaia_members", "").replace("_", "")
        )
        data[name] = numpy.genfromtxt(fname, names=names, skip_header=1)

    return data


def parse_deBoer_2019_stitched_profiles(logger, dirname="{0}stitched_profiles/".format(BASEDIR)):
    if not os.path.exists(dirname) or not os.path.isdir(dirname):
        logger.error("ERROR: dir not found: {0}".format(dirname))
        return

    files = [f for f in glob.glob(dirname+"*") if "pdf" not in f]
    names = [
        "rad", "density", "density_err"
    ]

    data = dict()
    for fname in files:
        name = fix_gc_names(
            fname.split("stitched_profiles/")[-1].replace(
                "_numdens_profile", "").replace("_", "")
        )
        data[name] = numpy.genfromtxt(fname, names=names)

    return data


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger = logging.getLogger(__file__)
    logger.info("Running {0}".format(__file__))

    deBoer_fits = parse_deBoer_2019_fits(logger)
    logger.info("\nde Boer (2019) fits")
    logger.info(deBoer_fits.shape)
    logger.info(deBoer_fits.dtype)
    logger.info(deBoer_fits["id"])

    # TODO: do we want to do something /w member star catalogue?
    # deBoer_member_stars = parse_deBoer_2019_member_stars(logger)
    # logger.info("\nde Boer (2019) member stars")
    # logger.info(len(deBoer_member_stars))
    # logger.info(deBoer_member_stars["NGC 1261"].shape)
    # logger.info(deBoer_member_stars["NGC 1261"].dtype)
    # logger.info(deBoer_member_stars.keys())

    deBoer_stitched_profiles = parse_deBoer_2019_stitched_profiles(logger)
    logger.info("\nde Boer (2019) stitched profiles")
    logger.info(len(deBoer_stitched_profiles))
    logger.info(deBoer_stitched_profiles["NGC 1261"].shape)
    logger.info(deBoer_stitched_profiles["NGC 1261"].dtype)
    logger.info(deBoer_stitched_profiles.keys())
