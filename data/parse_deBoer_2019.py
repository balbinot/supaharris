import os
import sys
import glob
import numpy
import logging
import matplotlib
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


def plot_deBoer_2019(logger, deBoer_fit, deBoer_stitched_profiles, fig=None,
        show_King=True, show_Wilson=True, show_limepy=True, show_spes=True,
        show_BGlev=True, show_rtie=True, show_rJ=True, has_tex=True, verbose=False):

    try:
        import limepy
    except ImportError:
        logger.error("ERROR: plot_deBoer_2019 requires limepy, but it is not installed.")
        return

    if fig is None:
        fig, ax = pyplot.subplots(1, 1, figsize=(12, 12))
    else:
        ax = pyplot.gca()

    # Plot the deBoer2019 stitched profile
    gc_name = deBoer_fit["id"]
    ax.text(0.5, 1.01, gc_name, ha="center", va="bottom", transform=ax.transAxes)

    n0 = deBoer_stitched_profiles[gc_name]["density"][0]  # central number density
    Ntotal = deBoer_stitched_profiles[gc_name]["density"].sum()
    logger.info("\n{0} has {1} stars".format(gc_name, Ntotal))
    ax.errorbar(
        deBoer_stitched_profiles[gc_name]["rad"],
        deBoer_stitched_profiles[gc_name]["density"],
        yerr=deBoer_stitched_profiles[gc_name]["density_err"],
        marker="o", c="g", ls="", ms=4, elinewidth=2, markeredgewidth=2, capsize=5
    )

    # Get the distance
    from data.parse_harris_1996ed2010 import parse_harris1996ed2010
    h96_gc = parse_harris1996ed2010(logger)
    distance_kpc = h96_gc[gc_name].dist_from_sun
    logger.info("{0}'s distance from Sun is {1:.2f} kpc (Harris 1996, 2010 ed.)".format(
        gc_name, distance_kpc))

    # Get the Jacobi radius from Balbinot & Gieles (2018)
    from utils import parsec2arcmin
    from utils import arcmin2parsec
    from data.parse_balbinot_2018 import parse_balbinot_2018
    b18 = parse_balbinot_2018(logger)
    imatch, = numpy.where(b18["Name"] == gc_name)[0]
    rJ = parsec2arcmin(b18[imatch]["r_J"], distance_kpc)
    logger.info("{0} has Jacobi radius {1:.2f}' (Balbinot & Gieles 2018)\n".format(
        gc_name, rJ))

    # Overplot the best-fit King (1966) model
    if show_King:
        for king_param in [
            "W_king", "rt_king", "M_king"
        ]:
            if verbose:
                logger.info("{0:<20s}{1:> 15.3f} +/- {2:>7.3f}".format(
                    king_param, deBoer_fit[king_param], deBoer_fit["e_"+king_param])
                )
        if verbose:
            logger.debug("{0:<20s}{1:> 15.3f}".format("kinghalf", deBoer_fit["kinghalf"]))
            logger.debug("{0:<20s}{1:> 15.3f}".format("kingtrunc", deBoer_fit["kingtrunc"]))
            logger.debug("{0:<20s}{1:> 15.3f}".format("chi2_king", deBoer_fit["chi2_king"]))
            logger.debug("{0:<20s}{1:> 15.3f}\n".format("chi2red_king", deBoer_fit["chi2red_king"]))
        # W must be phi0: central dimensionless potential
        # g: Order of truncation (0<= g < 3.5; 0=Woolley, 1=King, 2=Wilson)
        rt_king = parsec2arcmin(deBoer_fit["rt_king"], distance_kpc)
        k = limepy.limepy(deBoer_fit["W_king"], g=1, nrt=25*rJ/rt_king,
            M=deBoer_fit["M_king"], rt=rt_king, project=True, verbose=verbose)
        if verbose:
            logger.debug("{0:<20s}{1:> 15.3f}".format("King", k.r0))
            logger.debug("{0:<20s}{1:> 15.3f}".format("Half-mass", k.rh))
            logger.debug("{0:<20s}{1:> 15.3f}".format("virial", k.rv))
            logger.debug("{0:<20s}{1:> 15.3f}\n".format("truncation", k.rt))

        # The profile is sampled up to 3*rt by default, but deBoer+ 2019 Figure 6
        # and Figure A1-A14 show the sampled profiles down to BGlev
        BGlev = numpy.argwhere(k.Sigma <= deBoer_fit["BGlev"])
        k.Sigma[BGlev] = deBoer_fit["BGlev"]
        ax.plot(k.R, k.Sigma, c="b", ls=":", lw=2, label="King")


    if show_Wilson:
        for wilson_param in [
            "W_wil", "rt_wil", "M_wil"
        ]:
            if verbose:
                logger.debug("{0:<20s}{1:> 15.3f} +/- {2:>7.3f}".format(
                    wilson_param, deBoer_fit[wilson_param], deBoer_fit["e_"+wilson_param])
                )
        if verbose:
            logger.debug("{0:<20s}{1:> 15.3f}".format("wilhalf", deBoer_fit["wilhalf"]))
            logger.debug("{0:<20s}{1:> 15.3f}".format("wiltrunc", deBoer_fit["wiltrunc"]))
            logger.debug("{0:<20s}{1:> 15.3f}".format("chi2_wil", deBoer_fit["chi2_wil"]))
            logger.debug("{0:<20s}{1:> 15.3f}\n".format("chi2red_wil", deBoer_fit["chi2red_wil"]))
        # W must be phi0: central dimensionless potential
        # g: Order of truncation (0<= g < 3.5; 0=Woolley, 1=King, 2=Wilson)
        rt_wilson = parsec2arcmin(deBoer_fit["rt_wil"], distance_kpc)
        w = limepy.limepy(deBoer_fit["W_wil"], g=2, M=deBoer_fit["M_wil"],
            rt=rt_wilson, nrt=25*rJ/rt_wilson, project=True, verbose=verbose)
        if verbose:
            logger.debug("{0:<20s}{1:> 15.3f}".format("King", w.r0))
            logger.debug("{0:<20s}{1:> 15.3f}".format("Half-mass", w.rh))
            logger.debug("{0:<20s}{1:> 15.3f}".format("virial", w.rv))
            logger.debug("{0:<20s}{1:> 15.3f}\n".format("truncation", w.rt))

        BGlev = numpy.argwhere(w.Sigma <= deBoer_fit["BGlev"])
        w.Sigma[BGlev] = deBoer_fit["BGlev"]
        ax.plot(w.R, w.Sigma, c="g", ls="-.", lw=2, label="Wilson")


    if show_limepy:
        # LIMEPY: (Multi-Mass, Anisotropic) Lowered Isothermal Model Explorer in Python
        for lime_param in [
            "W_lime", "g_lime", "rt_lime", "M_lime", "limehalf"
        ]:
            logger.debug("{0:<20s}{1:> 15.3f} +/- {2:>7.3f}".format(
                lime_param, deBoer_fit[lime_param], deBoer_fit["e_"+lime_param])
            )
        logger.debug("{0:<20s}{1:> 15.3f}".format("chi2_lime", deBoer_fit["chi2_lime"]))
        logger.debug("{0:<20s}{1:> 15.3f}\n".format("chi2red_lime", deBoer_fit["chi2red_lime"]))
        # W must be phi0: central dimensionless potential
        # g: order of truncation (0<= g < 3.5; 0=Woolley, 1=King, 2=Wilson)
        rt_lime = parsec2arcmin(deBoer_fit["rt_lime"], distance_kpc)
        l = limepy.limepy(deBoer_fit["W_lime"], g=deBoer_fit["g_lime"],
            M=deBoer_fit["M_lime"], rt=rt_lime, nrt=25*rJ/rt_lime,
            project=True, verbose=verbose)
        logger.debug("{0:<20s}{1:> 15.3f}".format("King", l.r0))
        logger.debug("{0:<20s}{1:> 15.3f}".format("Half-mass", l.rh))
        logger.debug("{0:<20s}{1:> 15.3f}".format("virial", l.rv))
        logger.debug("{0:<20s}{1:> 15.3f}\n".format("truncation", l.rt))

        BGlev = numpy.argwhere(l.Sigma <= deBoer_fit["BGlev"])
        l.Sigma[BGlev] = deBoer_fit["BGlev"]
        ax.plot(l.R, l.Sigma, c="k", ls="--", lw=2,
            label="$\\textsc{limepy}$" if has_tex else "limepy")


    if show_spes:
        # SPES: Spherical Potential Escapers Stitched models
        B = 1 - numpy.power(10, deBoer_fit["log1minB_pe"])
        e_B = 1 - numpy.power(10, deBoer_fit["e_log1minB_pe"])
        fpe = numpy.power(10, deBoer_fit["log_fpe"])
        e_fpe = numpy.power(10, deBoer_fit["e_log_fpe"])
        for pe_param in [
            "W_pe", "eta_pe", "log1minB_pe", "rt_pe", "M_pe", "pecore", "log_fpe", "pehalf"
        ]:
            if verbose:
                logger.debug("{0:<20s}{1:> 15.3f} +/- {2:>7.3f}".format(
                    pe_param, deBoer_fit[pe_param], deBoer_fit["e_"+pe_param])
                )
                if pe_param == "log1minB_pe":
                    logger.debug("{0:<20s}{1:> 15.3f} +/- {2:>7.3f}".format("B", B, e_B))
        if verbose:
            logger.debug("{0:<20s}{1:> 15.3f}".format("chi2_pe", deBoer_fit["chi2_pe"]))
            logger.debug("{0:<20s}{1:> 15.3f}\n".format("chi2red_pe", deBoer_fit["chi2red_pe"]))
        # W must be phi0: central dimensionless potential
        # eta: velocity dispersion of PEs in model units [0-1]
        # B: reduction of the DF at trunction [0-1]
        rt_spes = parsec2arcmin(deBoer_fit["rt_pe"], distance_kpc)
        s = limepy.spes(deBoer_fit["W_pe"], B=B, eta=deBoer_fit["eta_pe"],
            M=deBoer_fit["M_pe"], fpe=fpe, rt=rt_spes, nrt=25*rJ/rt_spes,
            project=True, verbose=verbose)

        if verbose:
            logger.debug("{0:<20s}{1:> 15.3f}".format("King", s.r0))
            logger.debug("{0:<20s}{1:> 15.3f}".format("Half-mass", s.rh))
            logger.debug("{0:<20s}{1:> 15.3f}".format("virial", s.rv))
            logger.debug("{0:<20s}{1:> 15.3f}\n".format("truncation", s.rt))

        BGlev = numpy.argwhere(s.Sigma <= deBoer_fit["BGlev"])
        s.Sigma[BGlev] = deBoer_fit["BGlev"]
        ax.plot(s.R, s.Sigma, c="r", ls="-", lw=2,
            label="$\\textsc{spes}$" if has_tex else "spes")

    # Indicate the background level
    if show_BGlev:
        ax.axhline(deBoer_fit["BGlev"], c="k", ls="--", lw=2)

    trans = matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes)
    if show_rtie:
        # Indicate the Gaia completeness radius at which the data was stitched
        ax.vlines(deBoer_fit["r_tie"], ymin=deBoer_fit["BGlev"]/25,
            ymax=deBoer_fit["BGlev"], lw=3)
        ax.text(deBoer_fit["r_tie"], 0.01, r"$\textit{Gaia}$ complete"
            if has_tex else "Gaia Complete",
            fontsize=16, ha="left", va="bottom", transform=trans)

    if show_rJ:
        # Jacobi radius
        ax.axvline(rJ, c="k", ls="--", lw=2)
        ax.text(rJ, 1.0, "$r_J$ = {:.1f}'".format(rJ), fontsize=16,
            ha="center", va="bottom", transform=trans)

    ax.set_xlim(0.5*deBoer_stitched_profiles[gc_name]["rad"][0], 5*rJ)
    ax.set_ylim(0.1*deBoer_fit["BGlev"], 2*deBoer_stitched_profiles[gc_name]["density"].max())
    # ax.set_ylim(1e-3, 1e5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("$R$ [arcmin]")
    ax.set_ylabel("$n_{Gaia}$ [arcmin$^{-2}$]")
    ax.legend(fontsize=16, loc="upper right", frameon=True)

    return fig


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger = logging.getLogger(__file__)
    logger.info("Running {0}".format(__file__))

    sys.path.insert(0, "/supaharris")
    from utils import parsec2arcmin
    from utils import arcmin2parsec

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

    from plotsettings import *
    from matplotlib import pyplot
    pyplot.switch_backend("agg")
    for i, fit in enumerate(deBoer_fits):
        if fit["id"] != "NGC 1261": continue
        fig, ax = pyplot.subplots(1, 1, figsize=(10, 10))
        fig = plot_deBoer_2019(logger, fit, deBoer_stitched_profiles, fig=fig, has_tex=False)
        fig.savefig("{0}/{1}.pdf".format(BASEDIR, fit["id"]))
        pyplot.close(fig)
