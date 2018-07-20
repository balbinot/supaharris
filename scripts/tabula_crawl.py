#!/usr/bin/env python
#-*- coding: utf-8 -*-

import tabula as tb
from pdfsources import bdir, sources

for sn,v in sources.iteritems():
    df = tb.read_pdf(bdir+v['file'], pages=v['pages'])
    print df
    print sn, v['pages']



