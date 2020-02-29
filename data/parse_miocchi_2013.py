import os
import sys
import glob
import numpy
import scipy
import logging
import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot
from urllib.parse import urlparse


BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_GCS_Miocchi2013/"


def fix_gc_names(name):
    if name == "ERIDANU" or name == "ERIDANUS":
        name = "Eridanus"
    name = name.replace("PAL", "Pal ")
    name = name.replace("TER", "Terzan ").replace("ZAN", "")
    name = name.replace("AM", "AM ")
    name = name.replace("NGC", "NGC ")

    try:
        ngc = float(name)
        name = "NGC " + name
    except ValueError:
        pass

    return name


def scrape_profiles_from_cosmiclab_website(logger, force=False):
    base_url = "http://www.cosmic-lab.eu/catalog/"

    # Get index
    r = requests.get(base_url + "index.php")
    if r.status_code != 200:
        logger.error("ERROR: could not retrieve {0}".format(clusterlist))
        return
    soup = BeautifulSoup(r.content, "lxml")
    # Find url for each globular cluster
    profile_urls = [base_url + a["href"]
        for a in soup.find("table", id="catalog").find_all("a")]

    # Visit page for each globular cluster, grab the data file
    for profile_url in profile_urls:
        r = requests.get(profile_url)
        if r.status_code != 200:
            logger.error("ERROR: could not retrieve {0}".format(clusterlist))
            return
        soup = BeautifulSoup(r.content, "lxml")
        download_url = base_url + soup.find("a", class_="FT_link")["href"]
        plot_url = base_url + soup.find("img", class_="plot")["src"]

        logger.info("Downloading: {0}".format(download_url))
        data = requests.get(download_url).content.decode("ascii")
        cluster_name = data.split("# cluster:")[-1].split("\n")[0].strip()
        if " " in cluster_name:
            cluster_name = cluster_name.split(" ")[0]
        fname = "{0}{1}.dat".format(BASEDIR, cluster_name)
        if (not os.path.exists(fname) and not os.path.isfile(fname)) or force:
            logger.info("Saving as: {0}\n".format(fname))
            with open(fname, "wb") as f:
                f.write(data.encode("utf-8"))
        else:
            logger.debug("Already have: {0}\n".format(fname))

        logger.info("Downloading: {0}".format(plot_url))
        fname = "{0}{1}.jpg".format(BASEDIR, cluster_name)
        if (not os.path.exists(fname) and not os.path.isfile(fname)) or force:
            logger.info("Saving as: {0}\n".format(fname))
            r = requests.get(plot_url, stream=True)
            if r.status_code != 200:
                logger.error("  ERROR: could not retrieve {0}".format(plot_url))
                import sys; sys.exit(1)
            with open(fname, "wb") as f:
                for chunk in r:  # reads the data in chunks of 128 bytes
                    f.write(chunk)
        else:
            logger.info("Already have: {0}\n".format(fname))


def parse_miocchi_2013_table2(logger, fname="{0}table2.txt".format(BASEDIR)):
    url = "http://www.cosmic-lab.eu/catalog/table2.dat"
    if not os.path.exists(fname) or not os.path.isfile(fname):
        logger.info("Downloading: {0}".format(url))
        logger.info("Saving to: {0}\n".format(fname))
        data = requests.get(url).content.decode("ascii")
        with open(fname, "wb") as f:
            f.write(data.encode("utf-8"))
    else:
        logger.info("Already have: {0}\n".format(fname))

    # Read the data, dump in lists
    with open(fname, "r") as f:
        data = f.readlines()
    header = data[0:15]
    body = data[15:-1]
    clean_data = []
    for i, row in enumerate(body):
        if row.startswith("##"): continue
        clean_data.append(row.split())

    # Convert to structured array
    names = [
        "NGCno.", "mod", "W0", "+dW0", "-dW0", "rc", "+drc", "-drc", "r0",
        "+dr0", "-dr0", "c0", "+dc0", "-dc0", "rl", "+drl", "-drl",
        "rhm", "+drhm", "-drhm", "re", "+dre", "-dre", "N_BG", "chi2_nu"
    ]
    formats = ["f8" for n in names]; formats[0] = "U16"; formats[1] = "U1"
    dtype = {"names": names, "formats": formats}
    structured = numpy.empty(len(clean_data), dtype=dtype)
    for i, row in enumerate(clean_data):
        for col_name, col_value in zip(names, row):
            structured[i][col_name] = col_value

    for i, name in enumerate(structured["NGCno."]):
        structured[i]["NGCno."] = fix_gc_names(name)

    return structured


def parse_miocchi_2013_profiles(logger):
    data = dict()
    dtype = {
        "names": ["radius", "log_surface_density", "err_log_surface_density"],
        "formats": ["f8", "f8", "f8"]
    }
    for fname in glob.glob(BASEDIR+"*"):
        if "table2" in fname: continue
        if "jpg" in fname: continue

        with open(fname) as f:
            raw = f.readlines()
        header = raw[0:2]
        body = raw[2:]

        cluster_name = str(header).split("# cluster:")[-1].split("\n")[0].strip()
        if " " in cluster_name:
            cluster_name = cluster_name.split(" ")[0]
        cluster_name = fix_gc_names(cluster_name)
        logger.debug("Found profile for GC: {0}".format(cluster_name))

        profile = numpy.zeros(len(body), dtype=dtype)
        for i, row in enumerate(body):
            col = row.split()
            profile[i]["radius"] = col[0]
            profile[i]["log_surface_density"] = col[1]
            profile[i]["err_log_surface_density"] = col[2]

        data[cluster_name] = profile
    return data


def plot_miocchi_2013(m13_t2, m13_profs, cluster_name):
    import limepy

    fig, (ax1, ax2) = pyplot.subplots(2, 1, figsize=(7, 9),
        sharex=True, gridspec_kw={"height_ratios": [7,2]})

    ax1.text(0.5, 1.0, cluster_name, ha="center", va="bottom", transform=ax1.transAxes)

    gc = m13_profs[cluster_name]
    imatch, = numpy.where(m13_t2["NGCno."] == cluster_name)
    iking, = numpy.where(m13_t2[imatch]["mod"] == "K")
    iwilson, = numpy.where(m13_t2[imatch]["mod"] == "W")
    king = m13_t2[imatch][iking]
    wilson = m13_t2[imatch][iwilson]

    ax1.errorbar(numpy.log10(gc["radius"]), gc["log_surface_density"],
        yerr=gc["err_log_surface_density"], marker="o", fillstyle="none",
        c="k", ls="", ms=5, elinewidth=2, markeredgewidth=2, capsize=5
    )
    k = limepy.limepy(king["W0"], g=1, rt=king["rl"], project=True)
    k_interp1d = scipy.interpolate.interp1d(k.R, numpy.log10(k.Sigma))
    # TODO: how to convert limepy models from projected mass density to star counts?
    # Now we hack this by taking the ratio of ObservedStarCount_0 (mean of innermost
    # 3 bins) and Sigma_0 (evaluated at the radii of the innermost 3 bins) of the
    # interp1d representation of the limepy profile. We use the interp1d representation
    # of limepy b/c the innermost radii differ.
    k_magic = numpy.mean(gc["log_surface_density"][0:3])
    k_magic -= numpy.mean(k_interp1d(gc["radius"][0:3]))
    ax1.plot(numpy.log10(k.R), numpy.log10(k.Sigma)+k_magic, c="k", ls="-", lw=2)

    w = limepy.limepy(wilson["W0"], g=2, rt=wilson["rl"], project=True)
    w_interp1d = scipy.interpolate.interp1d(w.R, numpy.log10(w.Sigma))
    w_magic = numpy.mean(gc["log_surface_density"][0:3])
    w_magic -= numpy.mean(w_interp1d(gc["radius"][0:3]))
    ax1.plot(numpy.log10(w.R), numpy.log10(w.Sigma)+w_magic, c="k", ls="--", lw=2)

    # Add the residuals
    rvalid, = numpy.where(gc["radius"] <= k.R.max())
    # Interpolate again /w rescaled profile
    k_interp1d = scipy.interpolate.interp1d(k.R, numpy.log10(k.Sigma)+k_magic)
    ax1.plot(numpy.log10(gc["radius"][rvalid]), k_interp1d(gc["radius"][rvalid]), "ro", ms=4)
    k_residuals = k_interp1d(gc["radius"][rvalid]) - gc["log_surface_density"][rvalid]
    k_residuals /= gc["log_surface_density"][rvalid]
    ax2.plot(numpy.log10(gc["radius"][rvalid]), k_residuals, "ro", ms=4)

    rvalid, = numpy.where(gc["radius"] <= w.R.max())
    w_interp1d = scipy.interpolate.interp1d(w.R, numpy.log10(w.Sigma)+w_magic)
    ax1.plot(numpy.log10(gc["radius"][rvalid]), w_interp1d(gc["radius"][rvalid]), "bo", ms=4)
    w_residuals = w_interp1d(gc["radius"][rvalid]) - gc["log_surface_density"][rvalid]
    w_residuals /= gc["log_surface_density"][rvalid]
    ax2.plot(numpy.log10(gc["radius"][rvalid]), w_residuals, "bo", ms=4)

    ax2.axhline(0, c="k", lw=1)
    klim = max(numpy.abs(k_residuals.min()), numpy.abs(k_residuals.max()))
    wlim = max(numpy.abs(w_residuals.min()), numpy.abs(w_residuals.max()))
    ylim = 1.1*max(klim, wlim)
    if ylim > 2:
        ylim = 2
    ax2.set_ylim(-ylim, ylim)

    ax1.set_ylabel("log $\Sigma_*$(r) [arcsec$^{-2}$]")
    ax2.set_xlabel("log(r/arcsec)")

    for ax in fig.axes:
        ax.set_xticks(range(-1, 6, 1))
        ax.set_xticks(numpy.arange(-1, 6, 0.2), minor=True)
        ax.set_xlim(0.9*numpy.log10(gc["radius"]).min(), 1.1*numpy.log10(gc["radius"].max()))
    ax1.set_yticks(range(-6, 6, 1))
    ax1.set_yticks(numpy.arange(-6, 6, 0.2), minor=True)
    ymin = gc["log_surface_density"].min()
    ymax = gc["log_surface_density"].max()
    ax1.set_ylim(1.1*ymin, 1.25*ymax if ymax>0 else 0.75*ymax)

    pyplot.subplots_adjust(hspace=0)
    pyplot.show(fig)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger = logging.getLogger(__file__)
    logger.info("Running {0}".format(__file__))

    scrape_profiles_from_cosmiclab_website(logger)

    m13_t2 = parse_miocchi_2013_table2(logger)
    print("shape: {0}; length: {1}\n".format(m13_t2.shape, len(m13_t2)))
    print("dtype: {0}\n".format(m13_t2.dtype))
    print("first row: {0}\n".format(m13_t2[0]))
    print("clusters:\n{0}\n".format(m13_t2["NGCno."]))

    m13_profs = parse_miocchi_2013_profiles(logger)
    print("clusters:\n{0}".format(list(m13_profs.keys())))

    for cluster_name in m13_profs.keys():
        plot_miocchi_2013(m13_t2, m13_profs, cluster_name)
