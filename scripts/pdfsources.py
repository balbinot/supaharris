#!/usr/bin/env python
# -*- coding: utf-8 -*-

bdir = "data/"

sources = {
    "Dias+15": {
        "doi": "10.1051/0004-6361/201526765",
        "ads": "2016A%26A...590A...9D",
        "file": "aa26765-15.pdf",
        "type": "original",
        "pages": "15",
        "cols": ["Cluster", "vhelio", "[Fe/H]*", "[Mg/Fe]", "[α/Fe]"],
        "alias": ["cname", "V_r", "feh", "mgfe", "afe"],
        "ctype": ["s", "ve", "ve", "ve", "ve"],
        "skip": 1,
        "condition": "",
    },
    "Carretta+09": {
        "doi": "10.1051/0004-6361/200913003",
        "ads": "2009A&A...508..695C",
        "file": "aa13003-09.pdf",
        "type": "original/compilation",
        "pages": "15",
        "cols": ["GC", "[Fe/H]", "err", "Note", "GC", "[Fe/H]", "err", "Note"],
        "alias": ["cname", "feh", "efeh", "note", "cname", "feh", "efeh", "note"],
        "ctype": ["s", "v", "e", "s", "s", "v", "e", "s"],
        "skip": 1,
        "condition": "Note == 1",
    },
    "Goldsbury+10": {
        "doi": "10.1088/0004-6256/140/6/1830",
        "ads": "2010AJ....140.1830G",
        "file": "Go10.pdf",
        "type": "original",
        "pages": "9-10",
        "cols": ["Cluster ID", "R.A. J2000", "Decl. J2000", "Estimated"],
        "alias": ["cname", "RAstr", "Decstr", "eRA"],
        "ctype": ["s", "v", "v", "e"],
        "skip": 1,
        "condition": "",
    },
}
