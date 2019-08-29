import os
import sys
import numpy
import logging
from io import StringIO
from matplotlib import pyplot

from catalogue.models import Reference


logger = logging.getLogger("console")
logger.logLevel = logging.DEBUG

BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_StarClusters_Bica2019/"


def parse_bica_2019_refs(fname="{0}refs.dat".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.debug("ERROR: file not found: {0}".format(fname))
        return

    nrefs, references = 0, list()
    with open(fname, "r") as f:
        for line in f.readlines(): nrefs += 1
    with open(fname, "r") as f:
        for i, line in enumerate(f.readlines()):
            ref_code = line[0:7].strip()
            ref = line[8:365].strip()
            bib_code = line[366:385].strip()
            cat = line[386:396].strip()
            ads_url = "https://ui.adsabs.harvard.edu/abs/{0}".format(bib_code)

            logger.debug("Entry {0}/{1}".format(i+1, nrefs))
            logger.debug("  ref_code: {0}".format(ref_code))
            logger.debug("  ref: {0}".format(ref))
            logger.debug("  bib_code: {0}".format(bib_code))
            logger.debug("  cat: {0}".format(cat))

            if bib_code == "-------------------":
                reference, created = Reference.objects.get_or_create(
                    ads_url="https://example.com/{0}".format(ref_code),
                    bib_code=ref_code,
                )
                reference.title = ref; reference.save()
                setattr(Reference, ref_code, reference)
                references.append(ref_code)
            else:
                reference, created = Reference.objects.get_or_create(ads_url=ads_url)
                setattr(Reference, ref_code, reference)
                references.append(ref_code)

            if not created:
                logger.info("Found the Reference: {0}\n".format(ref_code))
            else:
                logger.info("Created the Reference: {0}\n".format(ref_code))

            # if i > 35: break

    return references


def parse_bica_2019_table2(fname="{0}table2.dat".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return


def parse_bica_2019_table3(fname="{0}table3.dat.gz".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return


def parse_bica_2019_table4(fname="{0}table4.dat".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return


def parse_bica_2019_table5(fname="{0}table5.dat".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return



if __name__ == "__main__":
    refs = parse_bica_2019_refs(debug=True)
    # t2 = parse_bica_2019_table2(debug=True)
    # t3 = parse_bica_2019_table3(debug=True)
    # t4 = parse_bica_2019_table4(debug=True)
    # t5 = parse_bica_2019_table5(debug=True)
