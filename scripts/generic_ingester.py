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
import numpy as np

# Django imports
from catalogue.models import *

cnames = np.array([o.cname.strip() for o in GlobularCluster.objects.all()])
rnames = np.array([o.rname.strip() for o in Reference.objects.all()])
pnames = np.array([o.pname.strip() for o in Parameter.objects.all()])
epnames = np.array(['e' + o.pname.strip() for o in Parameter.objects.all()])

#try:
#    r = Reference(rname='Trager et al.', doi='10.1086/118116', ads='add later')
#    r.save()
#except ValueError:
#    print('Reference already exists, using it')
#    r = Reference.objects.filter(rname='Trager et al.')[0]

def check_ref(rname):
    """
    Check if reference exists via fuzzy matching. If It does not exist create
    it.
    """

    b = process.extractOne(rname, rnames)
    if b[-1] >= 90:
        # TODO: this should be a multiple choice input with the highest
        # ranking fuzzy matches where DOI would be displayed as well.
        input('{} matched to {}; Continue? [Enter]'.format(b[0], rname))
        return(b[0])
    else:
        r = Reference(rname=rname, doi='', ads='')
        r.save()
        return(rname)

def get_pars(f):

    """
    Find parameters that are available in the DF as which match the ones
    already registered in the database.
    """

    pdict = {}
    pdict = dict.fromkeys(pnames, [])
    for colname in f.columns:
        j = (pnames == colname)
        ej = (epnames == colname)
        if any(j):
            print('Found {} in file header'.format(pnames[j]))
            pdict[pnames[j][0]] = pdict[pnames[j][0]] + [colname]
        elif any(ej):
            print('Found {} in file header as error column'.format(epnames[ej]))
            tmp = epnames[ej][0][1:]
            pdict[tmp] = pdict[tmp] + [colname]

        else:
            b = process.extractOne(colname, pnames)
            print('{} not found but matched to {} with rank {}'.format(colname,
                                                                       b[0],
                                                                       b[-1]))

    return(pdict)


# args is passed from manager.py runscripts --script-args ...
def run(*args):

    t = pd.ExcelFile(args[0])
    f = t.parse()
    f = f.fillna(np.nan)

    # Check if reference exists
    rname = check_ref(t.sheet_names[0])
    r = Reference.objects.filter(rname=rname)[0]

    # Build parameter dictionary
    pdict = get_pars(f)

    catnames = f.index
    for catname in catnames:
        b = process.extractOne(catname, cnames)
        if b[-1] > 90: ## sucess theshold for fuzzy matching
            c = GlobularCluster(cname=b[0])
            for k in pdict.keys():
                p = Parameter.objects.filter(pname=k)[0]
                if len(pdict[k])==3:
                    val = f.ix[b[0]][pdict[k][0]]
                    sigup = f.ix[b[0]][pdict[k][1]]
                    sigdown = f.ix[b[0]][pdict[k][2]]
                elif len(pdict[k])==2:
                    val = f.ix[b[0]][pdict[k][0]]
                    sigup = f.ix[b[0]][pdict[k][1]]
                    sigdown = sigup
                elif len(pdict[k])==1:
                    val = f.ix[b[0]][pdict[k][0]]
                    if val == np.nan:
                        val = None
                    sigup = None
                    sigdown = None
                else:
                    val = None

                if val != None and pd.notna(val):
                    o = Observation(pname=p, rname=r, cname=c, val=val,
                                    sigup=sigup, sigdown=sigdown)
                    print(o)
                    o.save()

    print(pdict)
