#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys

import numpy as np
import matplotlib.pyplot as p
from astroquery.vizier import Vizier
from astropy.table import Table

import os.path
from fuzzywuzzy import process
import json

from parse_trager import RP
from catalogue.models import *

f = RP()
tragernames = f.list()
f.list_cols()
dbnames = [u'NGC 6656', u'NGC 6342', u'NGC 6652', u'NGC 6717', u'NGC 6715', \
u'NGC 6712', u'UKS 1', u'NGC 5897', u'NGC 6093', u'NGC 6540', u'NGC 6528', u'NGC \
6325', u'NGC 6522', u'NGC 5053', u'NGC 6402', u'NGC 6401', u'Lynga 7', u'NGC \
5694', u'NGC 5272', u'FSR 1735', u'NGC 7089', u'NGC 6558', u'NGC 4372', u'NGC \
6496', u'NGC 6316', u'Ko 2', u'Ko 1', u'NGC 5286', u'NGC 6256', u'NGC 6254', \
u'NGC 6397', u'NGC 6144', u'NGC 362', u'NGC 6779', u'Ton 2', u'NGC 6553', u'NGC \
7006', u'NGC 5946', u'NGC 6304', u'Eridanus', u'NGC 6981', u'NGC 6544', u'NGC \
6541', u'Djorg 2', u'NGC 6266', u'2MS-GC02', u'NGC 6388', u'NGC 5466', \
u'1636-283', u'NGC 1904', u'NGC 6380', u'NGC 104', u'NGC 6171', u'NGC 6284', \
u'NGC 6287', u'NGC 6934', u'NGC 6760', u'ESO-SC06', u'NGC 7099', u'Liller 1', \
u'NGC 6440', u'NGC 6441', u'Pal 13', u'NGC 7078', u'NGC 6838', u'BH 176', \
u'Terzan 12', u'Terzan 10', u'NGC 5824', u'NGC 6273', u'AM 1', u'AM 4', u'NGC \
6864', u'NGC 1851', u'Arp 2', u'NGC 6453', u'NGC 6293', u'GLIMPSE01', \
u'GLIMPSE02', u'IC 1276', u'NGC 4833', u'NGC 5927', u'HP 1', u'Djorg 1', u'NGC \
6809', u'2MS-GC01', u'NGC 6637', u'NGC 3201', u'NGC 6681', u'NGC 6205', u'NGC \
6569', u'NGC 6341', u'NGC 6362', u'NGC 6366', u'Pyxis', u'NGC 6638', u'NGC \
4147', u'Pal 2', u'Pal 3', u'NGC 6426', u'Pal 1', u'Pal 6', u'Pal 4', u'Pal 5', \
u'NGC 6626', u'NGC 2808', u'Pal 8', u'NGC 5139', u'NGC 6584', u'Pal 14', u'Pal \
15', u'Pal 10', u'Pal 11', u'Pal 12', u'NGC 6218', u'NGC 2298', u'NGC 6356', \
u'NGC 6355', u'NGC 6352', u'NGC 6101', u'NGC 6517', u'NGC 6752', u'NGC 1261', \
u'NGC 7492', u'Terzan 1', u'Terzan 2', u'Terzan 3', u'Terzan 4', u'Terzan 5', \
u'Terzan 6', u'Terzan 7', u'Terzan 8', u'Terzan 9', u'NGC 5904', u'IC 1257', \
u'NGC 6139', u'IC 4499', u'NGC 288', u'NGC 2419', u'Whiting 1', u'NGC 6229', \
u'NGC 5986', u'Rup 106', u'NGC 6749', u'NGC 6624', u'NGC 6642', u'BH 261', u'NGC \
6723', u'NGC 6235', u'NGC 6121', u'NGC 5024', u'NGC 6333', u'NGC 5634', u'NGC \
6535', u'NGC 4590', u'E 3', u'NGC 6539']

print dbnames


