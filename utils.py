import ads
import json
import xlwt
import requests
import numpy as np
from bs4 import BeautifulSoup

from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse


# Convert ADS/arXiv-style month abbreviation to integers
MONTH_DICT = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


def export_to_xls(request, queryset):
    """ Generic method to export QuerySet of any Model instance to xls """

    model_fields= queryset[0]._meta.fields
    model_name = queryset[0]._meta.verbose_name_plural.title()

    xls = xlwt.Workbook(encoding='utf8')
    sheet = xls.add_sheet(model_name)

    # Define custom styles.
    borders = xlwt.easyxf('borders: top thin, right thin, bottom  thin, left thin;')
    boldborders = xlwt.easyxf('font: bold on; borders: top thin, right thin, bottom  thin, left thin;')

    row = 0  # Create header.
    for col, field in enumerate(model_fields):
        sheet.write(row, col, field.name, style=boldborders)

    for row, instance in enumerate(queryset):
        for col, field in enumerate(model_fields):
            try:
                value = str(getattr(instance, field.name, "")).encode('ascii', 'ignore')
            except UnicodeEncodeError:
                value = "UnicodeEncodeError"

            #The formatter cannot handle bytes type classes (unicode is not evaluated in bytes). Change to unicode if necessary
            if type(value) is bytes:
                value = value.decode('unicode_escape')

            # Do some cleanups
            if value == "None": value = ""

            sheet.write(row+1, col, value, style=borders)

    # # Return a response that allows to download the xls-file.
    now = timezone.now().strftime("%Y%m%d")
    filename = u'Export_{0}_{1}.xls'.format(model_name, now)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
    xls.save(response)
    return response


def requests_get(url, timeout=5, debug=settings.DEBUG, headers={}):
    try:
        r = requests.get(url, timeout=timeout, headers=headers)
    except requests.exceptions.Timeout:
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


def scrape_reference_details_from_arxiv(url, journals, debug=settings.DEBUG):
    if debug: print("Retrieving: {0}".format(url))
    r = requests_get(url, timeout=5)  # 5 seconds timeout
    if r is False: return False
    soup = BeautifulSoup(r.content, "lxml")

    details = dict()
    details["journal"] = "arxiv"
    details["title"] = soup.find("h1", class_="title").text.replace("Title:", "")
    details["authors"] = ", ".join([a.text for a in soup.find("div", class_="authors").find_all("a")])
    details["first_author"] = details["authors"].split(",")[0]

    # Example: "Submitted on DD MM YYYY"
    date = soup.find("div", class_="dateline").text.strip().replace("(", "").replace(")", "")
    if debug: print("  date: {0}".format(date))
    void, void, day, month, year = date.split(" ")
    try:
        details["month"] = MONTH_DICT[month.lower()]
    except KeyError:
        if debug:
            print("ERROR: key {0} not found in MONTH_DICT {1}".format(
                month.lower(), MONTH_DICT ))
        return False
    details["year"] = year

    # Convert full name of the journal to journal abbreviation
    journals_r = { v: k for k, v in journals.items() }
    details["journal"] = journals_r.get(details["journal"], details["journal"])

    if debug:
        print("Success!")
        [ print("  {0:<20s}: {1}".format(k, v)) for k,v in details.items() ]
    return details


def parse_bibtex_and_create_reference(relevant, journals, debug=settings.DEBUG):
    details = { line.split("=")[0].strip(): line.split("=")[1].strip(",").strip()
        for line in relevant }

    # Replace { bla }, but keep {} around last names
    details["authors"] = details["author"][1:-1]  # mind the extra s ;-)
    start, end = details["authors"].find("{"), details["authors"].find("}")
    details["first_author"] = details["authors"][start+1:end]

    # Remove {" bla "}
    details["title"] = details["title"][2:-2]

    # Clean up differences between new-style and old-style bibtex entry
    if "month" in details.keys():
        details["month"] = details["month"].lower().replace('"', '')
    if "year" in details.keys():
        details["year"] = int(details["year"].replace('"', ''))

    # Remove all {, }, and \\
    keys_available = list(details.keys())
    to_clean = ["adsnote", "adsurl", "doi", "journal", "keywords", "pages", "volume", "booktitle"]
    for key in list(set(keys_available).intersection(to_clean)):
        details[key] = details[key].strip().strip("{").strip("}").strip("\\")

    if "journal" not in details.keys():
        if "booktitle" in details.keys():
            # e.g. 1973BAAS....5..326M
            if details["booktitle"] in journals.keys():
                details["journal"] = details["booktitle"]
            else:
                details["journal"] = None
        else:
            details["journal"] = None

    # Convert full name of the journal to journal abbreviation
    journals_r = { v: k for k, v in journals.items() }
    if details["journal"] == "arXiv e-prints": details["journal"] = "arxiv"
    details["journal"] = journals_r.get(details["journal"], details["journal"])

    # Convert ADS-style month abbreviation to integers
    month_dict = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    details["month"] = month_dict.get(details.get("month", None), None)
    if details["month"]:
        details["month"] = int(details["month"])

    if debug:
        print("Success!")
        [ print("  {0:<20s}: {1}".format(k, v)) for k,v in details.items() ]

    return details


def scrape_reference_details_from_old_ads(url, journals, debug=settings.DEBUG):
    """ Here we obtain information for a Reference from old-style ADS' Bibtex entry """

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
    except IndexError as e:
        if str(e) == "list index out of range":
            return False
        else:
            raise

    r = requests_get(bibtex_url)
    if r is False: return False
    soup = BeautifulSoup(r.content, "lxml")
    relevant = [ split for split in soup.text.split("\n") if "=" in split ]
    return parse_bibtex_and_create_reference(relevant, journals, debug=debug)


def scrape_reference_details_from_new_ads(url, journals, timeout=5, debug=settings.DEBUG):
    """ Here we obtain information for a Reference from new-style ADS' Bibtex entry """

    payload = {"bibcode": [ url.split("abs/")[-1].split("/")[0] ]}
    if debug: print("Retrieving: {0}\n  payload: {1}".format(url, payload))

    headers = {
        "Authorization": "Bearer {0}".format(settings.ADS_API_TOKEN),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "user-agent": "Supaharris Bot v1.3.3.7"
    }
    try:
        r = requests.post(
            "https://api.adsabs.harvard.edu/v1/export/bibtex",
            params={"q":"*:*", "fl": "bibcode,title", "rows": 2000},
            data=json.dumps(payload), headers=headers, timeout=timeout,
        )
    except requests.exceptions.Timeout:
        if debug:
            print("ERROR: could not retrieve '{0}'".format(url) +
                " b/c requests.get timed out after {0} seconds".format(timeout))
        return False
    data = json.loads(r.content)

    if r is False or r.status_code != 200 or "export" not in data: return False
    # TODO: handle 429 with incremental back-off and max attempts

    relevant = [ split for split in data["export"].split("\n") if "=" in split ]
    return parse_bibtex_and_create_reference(relevant, journals, debug=debug)
