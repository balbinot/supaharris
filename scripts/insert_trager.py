#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supaharris.settings")

import numpy as np
import matplotlib.pyplot as p
from astroquery.vizier import Vizier
from astropy.table import Table

import os.path
from fuzzywuzzy import process
import json

from .parse_trager import RP
from catalogue.models import *

f = RP()
tragernames = f.list()
f.list_cols()

dbnames = [o.cname for o in GlobularCluster.objects.all()]
try:
    ## Create reference if does not exists
    r = Reference(rname='Trager et al. 1995', doi='10.1086/118116', ads='add later')
    r.save()
except:
    ## reference already exists
    r = Reference.objects.filter(rname='Trager et al.i 1995')[0]

def insert_into_django():
    # Emptying the tables
    for c in Profile.objects.all():
        c.delete()

    for query in dbnames:
        b = process.extractOne(query, tragernames)
        if b[-1] > 90: ## sucess theshold for fuzzy matching
            print('{} matched to {}; producing json'.format(b[0], query))
            tbl = f.get_rp(name=b[0])
            logr = tbl['logr']
            muV = tbl['muV']
            w = tbl['Weight']
            dset = tbl['DataSet']

            odict = {'log(r/arcmin)': logr.tolist(),
                     'mu_V': muV.tolist(),
                     'W': w.tolist(),
                     'label': dset.tolist(),}



            # Inserting a reference for the Harris Catalogue

            print('Inserting into database :')
            # Now add json to every matched cluster Profile model
            do = Profile()
            do.cname = GlobularCluster.objects.filter(cname=query)[0]
            print(do.cname)
            print(r)
            do.rname = r
            do.ptype = "Surface brightness profile"
            do.profile = json.dumps(odict)
            do.save()


        #cluster_id = models.ForeignKey(GlobularCluster, on_delete=models.CASCADE)
        #ptype      = models.CharField('Type of profile', max_length=256, null=True, blank=True)
        #profile    = JSONField('Profile')
        #modpars    = JSONField('Model parameters')
        #mtype      = models.CharField('Model flavour', max_length=256, null=True, blank=True)


insert_into_django()
