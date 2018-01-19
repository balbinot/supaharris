#-*- coding: utf-8 -*-
import sys
from astropy.coordinates import SkyCoord
from astropy import units as u

class HourAngle(object):
    def __init__(self, hh=None, mm=None, ss=None):
        self.hh = hh
        self.mm = mm
        self.ss = ss

    def from_str(self, s):
        s = s.strip()
        ps = s.find(' ')
        self.hh = int(s[:ps])
        s = s[ps:].strip()
        ps = s.find(' ')
        self.mm = int(s[:ps])
        s = s[ps:].strip()
        self.ss = float(s)

    def __str__(self):
        return ' {: 03d}:{:02d}:{:05.2f}'.format(self.hh, self.mm, self.ss)

class Cluster(object):
    def __init__(self):
        # General
        self.gid  = ''                         # Cluster identification
        self.name = None                       # Other commonly used cluster name

        # Coordinates
        self.ra                 = None         # Right ascension               (Epoch J2000)
        self.dec                = None         # Declination                   (Epoch J2000)
        self.gallon             = None         # Galactic longitude            (Degrees)
        self.gallat             = None         # Galactic latitude             (Degrees)
        self.dist_from_sun      = None         # Distance from sum             (kpc)

        # Metallicity
        self.metallicity        = None         # Metallicity [Fe/H]
        self.w_mean_met         = None         # Weight of mean metallicity

        # Photometry
        self.m_v_t              = None         # Cluster luminosity, M_V,t = V_t - (m-M)V
        self.ph_u_b             = None         # U-B
        self.ph_b_v             = None         # B-V
        self.ph_v_r             = None         # V-R
        self.ph_v_i             = None         # V-i
        self.ellipticity        = None         # Projected ellipticity of isophotes, e = 1-(b/a)

        # Velocities
        self.v_r                = None         # Heliocentric radial velocity (km/s)
        self.v_r_err            = None         # Observational uncertainty in radial velocity
        self.sig_v              = None         # Central velocity dispersion (km/s)
        self.sig_err            = None         # Observational uncertainty in velocity dispersion

        # Structural parameters
        self.sp_c               = None         # King-model central concentration, c=log(r_t/r_c)
        self.sp_r_c             = None         # Core radius (arcmin)
        self.sp_r_h             = None         # Half-light radius (arcmin)
        self.sp_mu_V            = None         # Central surface brightness (V magnitudes per arcsec^2)
        self.sp_rho_0           = None         # Central luminosity density, log_10(solar_lum/pc^3)

    def fill_in(self, do):
        if self.name:
            do.name = self.name
        if self.ra:
            do.ra  =  self.ra
            do.dec =  self.dec
        if self.gallon:
            do.gallon = self.gallon
            do.gallat  = self.gallat
        if self.dist_from_sun:
            do.dfs = self.dist_from_sun
        if self.metallicity:
            do.metallicity = self.metallicity
        if self.w_mean_met:
            do.w_mean_met = self.w_mean_met
        if self.m_v_t:
            do.m_v_t = self.m_v_t
        if self.ph_u_b:
            do.ph_u_b = self.ph_u_b
        if self.ph_b_v:
            do.ph_b_v = self.ph_b_v
        if self.ph_v_r:
            do.ph_v_r = self.ph_v_r
        if self.ph_v_i:
            do.ph_v_i = self.ph_v_i
        if self.ellipticity:
            do.ellipticity = self.ellipticity
        if self.v_r:
            do.v_r = self.v_r
            do.v_r_err = self.v_r_err
        if self.sig_v:
            do.sig_v = self.sig_v
            do.sig_err = self.sig_err
        if self.sp_c:
            do.sp_c = self.sp_c
        if self.sp_r_c:
            do.sp_r_c = self.sp_r_c
        if self.sp_r_h:
            do.sp_r_h = self.sp_r_h
        if self.sp_mu_V:
            do.sp_mu_V = self.sp_mu_V
        if self.sp_rho_0:
            do.sp_rho_0 = self.sp_rho_0

cluster_list = {}

def read_float(s):
    try:
        val = float(s.strip())
    except:
        val = None
    return val

def read_str(s):
    s = s.strip()
    return None if s == '' else s


# Ruler for f1
#0         1         2         3         4         5         6         7         8         9         100
#01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
# NGC 104    47 Tuc       00 24 05.67  -72 04 52.6   305.89  -44.89    4.5   7.4   1.9  -2.6  -3.1

# Parsing first file
f1 = open('import_data/f1.dat')
for line in f1:
    c = Cluster()
    c.gid               = line[:12].strip()
    c.name              = read_str(line[12:25])
    ra_str              = read_str(line[25:38])
    dec_str             = read_str(line[38:50])
    c.gallon         = read_float(line[50:58])
    c.gallat          = read_float(line[58:66])
    c.dist_from_sun     = read_float(line[66:73])
    #c.dist_from_gal_cen = read_float(line[73:79])
    #c.gal_dist_comp[0]  = read_float(line[79:85])
    #c.gal_dist_comp[1]  = read_float(line[85:91])
    #c.gal_dist_comp[2]  = read_float(line[91:])

    coo = SkyCoord(ra=ra_str, dec=dec_str, unit=(u.hourangle, u.degree))
    c.ra = coo.ra.deg
    c.dec = coo.dec.deg
    cluster_list[c.gid] = c

f1.close()

# Ruler for f2
#0         1         2         3         4         5         6         7         8         9         100
#01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
# NGC 104     -0.72 10   0.04 14.06 13.37  3.95  -9.42   0.37  0.88  0.53  1.14  G4    0.09

# Now parsing second file
f2 = open('import_data/f2.dat')
for line in f2:
    gid = line[:12].strip()
    c = cluster_list[gid]
    c.metallicity = read_float(line[13:18])
    c.w_mean_met  = read_float(line[18:21])
    #c.eb_v        = read_float(line[21:28])
    #c.v_hb        = read_float(line[28:34])
    #c.app_vd_mod  = read_float(line[34:40])
    #c.v_t         = read_float(line[40:46])
    c.m_v_t       = read_float(line[46:53])
    c.ph_u_b      = read_float(line[53:60])
    c.ph_b_v      = read_float(line[60:66])
    c.ph_v_r      = read_float(line[66:72])
    c.ph_v_i      = read_float(line[72:78])
    #c.spt         = read_str(line[78:82])
    c.ellipticity = read_float(line[82:])

f2.close()


# Ruler for f3
#0         1         2         3         4         5         6         7         8         9         100
#01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
# NGC 104      -18.0   0.1   -26.7    11.0   0.3   2.07      0.36  3.17   14.38   4.88   7.84  9.55

f3 = open('import_data/f3.dat')
for line in f3:
    gid = line[:12].strip()
    c = cluster_list[gid]

    c.v_r       = read_float(line[12:19])
    c.v_r_err   = read_float(line[19:25])
    #c.c_LSR     = read_float(line[25:33])
    c.sig_v     = read_float(line[33:41])
    c.sig_err   = read_float(line[41:47])
    c.c         = read_float(line[47:54])
    c.r_c       = read_float(line[54:64])
    c.r_h       = read_float(line[64:70])
    c.mu_V      = read_float(line[70:78])
    c.rho_0     = read_float(line[78:85])
    #c.lg_tc     = read_float(line[85:92])
    #c.lg_th     = read_float(line[92:])
f3.close()

import django
django.setup()
from catalogue.models import *

def insert_in_django():
    # Emptying the tables
    for c in GlobularCluster.objects.all():
        c.delete()

    for o in Observation.objects.all():
        o.delete()

    for r in Reference.objects.all():
        r.delete()

    # Inserting a reference for the Harris Catalogue
    r = Reference(name='Harris catalogue', doi='10.1086/118116', ads='')
    r.save()

    print('Inserting into database :')
    # Now creating the observations for every cluster:
    for c in cluster_list.values():
        print c
        dc = GlobularCluster(cluster_id = c.gid)
        print('  . {}'.format(c.gid))
        dc.save()

        do = Observation()
        do.cluster_id = dc
        do.ref = r
        c.fill_in(do)
        do.save()

