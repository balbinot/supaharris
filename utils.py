import requests
import numpy as np
from bs4 import BeautifulSoup

from django.conf import settings


def requests_get(url, timeout=5, debug=settings.DEBUG):
    try:
        r = requests.get(url, timeout=timeout)
    except requests.exceptions.TimeOut:
        if debug:
            print("ERROR: could not retrieve '{0}'".format(url) +
                " b/c requests.get timed out after {0} seconds".format(timeout))
        return False
    except requests.exceptions.RequestException as e:
        if debug:
            print("ERROR: could not retrieve '{0}'".format(url) +
                " b/c requests.get throws: {1}".format(url, e))
        return False

    return r


def scrape_reference_details_from_ads(url, journals, debug=settings.DEBUG):
    """ Here we obtain information for a Reference from ADS' Bibtex entry """

    if debug: print("Retrieving: {0}".format(url))
    r = requests_get(url, timeout=5)  # 5 seconds timeout
    if r is False: return False
    soup = BeautifulSoup(r.content, "lxml")

    try:
        bibtex_url = [a["href"] for a in soup.find_all("a")
            if "Bibtex entry for this abstract" in a.text][0]
        if debug: print("Get reference info from: {0}".format(bibtex_url))
    except KeyError as e:  # if ADS would have been updated
        return False

    r = requests_get(bibtex_url)
    if r is False: return False
    soup = BeautifulSoup(r.content, "lxml")
    relevant = [ split for split in soup.text.split("\n") if "=" in split ]
    details = { line.split("=")[0].strip(): line.split("=")[1].strip(",").strip()
        for line in relevant }

    # Replace { bla }, but keep {} around last names
    details["authors"] = details["author"][1:-1]  # mind the extra s ;-)
    start, end = details["authors"].find("{"), details["authors"].find("}")
    details["first_author"] = details["authors"][start+1:end]

    # Remove {" bla "}
    details["title"] = details["title"][2:-2]

    # Remove all {, }, and \\
    keys_available = list(details.keys())
    to_clean = ["adsnote", "adsurl", "doi", "journal", "keywords", "pages"]
    for key in list(set(keys_available).intersection(to_clean)):
        details[key] = details[key].strip().strip("{").strip("}").strip("\\")

    # Convert full name of the journal to journal abbreviation
    journals_r = { v: k for k, v in journals.items() }
    details["journal"] = journals_r.get(details["journal"], details["journal"])

    # Convert ADS-style month abbreviation to integers
    month_dict = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    try:
        details["month"] = month_dict[details["month"]]
    except KeyError:
        if debug:
            print("ERROR: key {0} not found in month_dict {1}".format(
                details["month"], month_dict))
        return False

    if debug:
        print("Success!")
        [ print("  {0:<20s}: {1}".format(k, v)) for k,v in details.items() ]
    return details
