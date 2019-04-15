#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.base")

import numpy as np
import matplotlib.pyplot as p
from astroquery.vizier import Vizier
from astropy.table import Table

import os.path
from fuzzywuzzy import process
import json

from catalogue.models import *

from glob import glob

tmp = glob('/home/eb0025/Dropbox/flames_proposal/GC_Gaia/*_numdens_profile')
tnames = [a.split('/')[-1].split('_')[0] for a in tmp]

dbnames = [o.cname for o in GlobularCluster.objects.all()]
try:
    ## Create reference if does not exists
    r = Reference(rname='de Boer et al. 2018', doi='', ads='')
    r.save()
except:
    ## reference already exists
    r = Reference.objects.filter(rname='de Boer et al. 2018')[0]

def insert_into_django():
    for query in dbnames:
        b = process.extractOne(query, tnames)
        if b[-1] > 90: ## sucess theshold for fuzzy matching
            print('{} matched to {}; producing json'.format(b[0], query))

            f = '/home/eb0025/Dropbox/flames_proposal/GC_Gaia/{}_numdens_profile'.format(b[0])

            r, dens, err = np.loadtxt(f, unpack=True)

            odict = {'r [arcmin]': r.tolist(),
                     'Density [/arcmin^2]': dens.tolist(),
                     'Unc': err.tolist(), }



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
            #do.save()


        #cluster_id = models.ForeignKey(GlobularCluster, on_delete=models.CASCADE)
        #ptype      = models.CharField('Type of profile', max_length=256, null=True, blank=True)
        #profile    = JSONField('Profile')
        #modpars    = JSONField('Model parameters')
        #mtype      = models.CharField('Model flavour', max_length=256, null=True, blank=True)


insert_into_django()
