#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from jsonfield import JSONField
#from django.contrib.auth.models import User

from schema import schema

UNIT_LENGTH = 32

VALIDATE = 1
ACCEPTED = 2
REJECTED = 3

STATUS_CHOICES = (
    (VALIDATE, 'To be validated'),
    (ACCEPTED, 'Accepted'),
    (REJECTED, 'Rejected'),
)

class GlobularCluster(models.Model):
    cluster_id = models.CharField(max_length=64)

    def __str__(self):
        return self.cluster_id

class Reference(models.Model):
    name     = models.CharField(max_length=256, null=True)
    doi      = models.CharField(max_length=256, null=True, blank=True)
    ads      = models.CharField(max_length=256, null=True, blank=True)
    pub_date = models.DateField('publication date', null=True)

    def __str__(self):
        s = ''
        if self.name:
            s += self.name
        return s

class Profile(models.Model):
    ref        = models.ForeignKey(Reference, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey(GlobularCluster, on_delete=models.CASCADE)
    ptype      = models.CharField('Type of profile', max_length=256, null=True, blank=True)
    profile    = JSONField('Profile')
    modpars    = JSONField('Model parameters')
    mtype      = models.CharField('Model flavour', max_length=256, null=True, blank=True)

class Observation(models.Model):
    ref        = models.ForeignKey(Reference, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey(GlobularCluster, on_delete=models.CASCADE)

    # General fields
    name = models.CharField('Alternate Name', max_length=64, null=True,
                            blank=True)

    schema = {'RA':  'Right Ascesion (J2000) [deg]',
              'Dec': 'Declination (J2000) [deg]',
              'l':   'Galactic longitude [deg]',
              'b':   'Galactic latittude [deg]',
              'D_sun': 'Heliocentric distance [kpc]',
              'D_GC':  'Galactocentric distance [kpc]',
              'X_helio': 'Heliocentric cartesian X component [kpc]',
              'Y_helio': 'Heliocentric cartesian Y component [kpc]',
              'Z_helio': 'Heliocentric cartesian Z component [kpc]',
              '[M/H]': 'Metallicity',
              'MV_t': 'Total V-band magnitude',
              'Luminosity': 'Total luminosity',
              'E(B-V)': 'Redenning',
              'Ellipticity': 'Ellipticity',
              'V_R': 'Radial velocity [km/s]',
              'sigmaV_R': 'Radial velocity dispersion [km/s]',
              'Concentration': 'King concentration parameter',
              'Core radius': 'King core radius [arcmin]',
              'Half-light radius': 'Half-light radius [arcmin]',
              'Central muV': 'mag/arcsec^2'}

    # Coordinates
    ra     = models.FloatField('RA', null=True, blank=True,
                               help_text=schema['RA'])
    dec    = models.FloatField('DEC', null=True, blank=True,
                               help_text=schema['Dec'])
    gallon = models.FloatField('l', null=True, blank=True, help_text=['l'])
    gallat = models.FloatField('b', null=True, blank=True, help_text=['b'])
    dfs       = models.FloatField('D_sun', null=True, blank=True,
                                  help_text=schema['D_sun'])
    dfgc      = models.FloatField('D_GC', null=True, blank=True,
                                  help_text=schema['D_GC'])

    x_helio = models.FloatField('X', null=True, blank=True,
                                help_text=schema['X_helio'])
    y_helio = models.FloatField('Y', null=True, blank=True,
                                help_text=schema['Y_helio'])
    z_helio = models.FloatField('Z', null=True, blank=True,
                                help_text=schema['Z_helio'])

    # Metallicity and Photometry
    metallicity = models.FloatField('[M/H]', null=True, blank=True,
                                    help_text=schema['[M/H]'])
    ebv   = models.FloatField('E(B-V)', null=True, blank=True,
                                 help_text=schema['E(B-V)'])
    MVt   = models.FloatField('MVt', null=True, blank=True,
                              help_text=schema['MV_t'])

    L     = models.FloatField('Luminosity', null=True, blank=True,
                              help_text=schema['Luminosity'])

    ellipticity = models.FloatField('Ellip', null=True, blank=True,
                                    help_text=schema['Ellipticity'])


    # Velocities
    v_r       = models.FloatField('Radial velocity', null=True, blank=True,
                                   help_text=schema['V_R'])
    ev_r      = models.FloatField('Radial velocity uncertainty', null=True,
                                   blank=True)
    sig_v     = models.FloatField('Velocity dispersion', null=True, blank=True,
                                   help_text=schema['sigmaV_R'])
    esig_v    = models.FloatField('Velocity dispersion uncertainty', null=True,
                                   blank=True)

    # Structural parameters
    c          = models.FloatField('Concentration', null=True, blank=True,
                                      help_text=schema['Concentration'])
    r_c        = models.FloatField('Core radius', null=True, blank=True,
                                      help_text=schema['Core radius'])
    r_h        = models.FloatField('Half-light radius', null=True,
                                      blank=True, help_text=schema['Half-light radius'])
    muV       = models.FloatField('Central surface brightness', null=True,
                                  blank=True, help_text=schema['Central muV'])

    comment = models.CharField('Additional comments', max_length=64, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=VALIDATE)


    def __str__(self):
        s = '{} - Ref : {}'.format(str(self.cluster_id), str(self.ref))
        return s
