#-*- coding: utf-8 -*-


"""

Check for

Reference name exists? ... ok
Parameter name exists? ... what about new pars? and Errors?
    Tricky. Make standardized from Harris work from Tom. Needs work...

Units ... leave to user


"""

import pandas as pd

from fuzzywuzzy import process


# Django imports
from catalogue.models import *

cnames = [o.cname for o in GlobularCluster.objects.all()]
rnames = [o.rname for o in Reference.objects.all()]
pnames = [o.pname for o in Parameter.objects.all()]

#try:
#    r = Reference(rname='Trager et al.', doi='10.1086/118116', ads='add later')
#    r.save()
#except ValueError:
#    print('Reference already exists, using it')
#    r = Reference.objects.filter(rname='Trager et al.')[0]


def check_ref(rname):

    b = process.extractOne(rname, rnames)
    print(b)
    if b[-1] >= 90:
        # TODO: this should be a multiple choice input with the highest
        # ranking fuzzy matches where DOI would be displayed as well.
        input('{} matched to {}; Continue? [Enter]'.format(b[0], rname))
        return(b[0])
    else:
        r = Reference(rname=rname, doi='', ads='')
        r.save()
        return(rname)


# args is passed from manager.py runscripts --script-args ...
def run(*args):

    t = pd.ExcelFile(args[0])
    rname = check_ref(t.sheet_names[0])
    print(rname)
    r = Reference.objects.filter(rname=rname)[0]

    f = t.parse()

    for colname in f.columns:
        b = process.extractOne(colname, pnames)
        if b[-1] >= 90:
            print('{} matched to {} with rank {}'.format(b[0], colname, b[-1]))
