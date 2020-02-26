import os
import sys
import glob
import numpy
import logging
import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot
from urllib.parse import urlparse


BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_GCS_Miocchi2013/"


def fix_gc_names(table2):
    for i, name in enumerate(table2["NGCno."]):
        name = name.replace("ERIDANU", "Eridanus")
        name = name.replace("PAL", "Pal ")
        name = name.replace("TER", "Terzan ")
        name = name.replace("AM", "AM ")

        try:
            ngc = float(name)
            name = "NGC " + name
        except ValueError:
            pass

        table2[i]["NGCno."] = name

    return table2


def scrape_profiles_from_cosmiclab_website(logger):
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
        logger.info("Downloading: {0}".format(download_url))

        data = requests.get(download_url).content.decode("ascii")
        cluster_name = data.split("# cluster:")[-1].split("\n")[0].strip()
        if " " in cluster_name:
            cluster_name = cluster_name.split(" ")[0]
        fname = "{0}{1}.dat".format(BASEDIR, cluster_name)
        logger.info("Saving as: {0}\n".format(fname))
        with open(fname, "wb") as f:
            f.write(data.encode("utf-8"))


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

    return fix_gc_names(structured)


def parse_miocchi_2013_profiles(logger):
    profiles = glob.glob(BASEDIR+"*")
    print(profiles)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
    logger = logging.getLogger(__file__)
    logger.info("Running {0}".format(__file__))

    scrape_profiles_from_cosmiclab_website(logger)

    data = parse_miocchi_2013_table2(logger)
    logger.debug("\ndata: {0}".format(data))

    profiles = parse_miocchi_2013_profiles(logger)
    logger.debug("\ndata: {0}".format(profiles))
