#!/usr/bin/env python
#-*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as p
from astroquery.vizier import Vizier
from astropy.table import Table

import os.path

class RP():
    def __init__(self):
        self.fname = 'trager.dat'
        if os.path.isfile(self.fname):
            self._load_data()
        else:
            self._fetch_data()
            self._write_data()

    def list(self):
        return np.unique(self.tbl['Name'])

    def list_cols(self):
        print self.tbl.keys()

    def get_rp(self, name='ngc2298'):
        j = (self.tbl['Name']==name)
        ntbl = self.tbl[:][j]
        return ntbl

    def _fetch_data(self):
        Vizier.ROW_LIMIT = -1
        catalog_list = Vizier.find_catalogs('Trager+ 1995')
        catalogs = Vizier.get_catalogs(catalog_list.keys())
        self.tbl = catalogs['J/AJ/109/218/tables']

    def _write_data(self):
        self.tbl.write(self.fname, format='ascii')

    def _load_data(self):
        self.tbl = Table.read(self.fname, format='ascii')

if __name__=='__main__':
    f = RP()
    f.list()
    f.list_cols()
    tbl = f.get_rp()
    logr = tbl['logr']
    muV = tbl['muV']
    w = tbl['Weight']
    dset = tbl['DataSet']

    ['Name', 'logr', 'muV', 'muVf', 'Resid', 'Weight', 'DataSet']



    import json
    odict = {'log(r/arcmin)': logr.tolist(),
             'mu_V': muV.tolist(),
             'W': w.tolist(),
             'label': dset.tolist(),}
    print json.dumps(odict)

    p.plot(logr, muV, 'ko')
    p.ylim(p.ylim()[::-1])
    p.xlabel('log(r/arcsec)')
    p.ylabel(r'$\mu_{V}$')
    p.show()


