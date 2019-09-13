#-*- coding: utf-8 -*-

import os
import sys
from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from catalogue.models import (
    Reference,
    Parameter,
    Observation,
    AstroObject,
    AstroObjectClassification,
)
from catalogue.utils import PrepareSupaHarrisDatabaseMixin
from data.parse_harris_1996ed2010 import parse_harris1996ed2010


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Harris data to the database"

    def handle(self, *args, **options):
        super().handle(*args, **options)  # to inherit the parent modifications

        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        ads_url = "https://ui.adsabs.harvard.edu/abs/1996AJ....112.1487H"
        harris1996ed2010, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}".format(harris1996ed2010))
        else:
            print("Created the Reference: {0}".format(harris1996ed2010))


        # Add classification(s)
        GC = AstroObjectClassification.objects.get(name="Globular Cluster")

        # Get the data. Note that save_as_xlsx requires openpyxl
        cluster_list = parse_harris1996ed2010(save_as_xlsx=False)

        # Keys: Values --> SupaHarris: Harris parameter names
        parameter_map = OrderedDict({
            # Coordinates
            "RA": "ra",                    # Right ascension               (Epoch J2000)
            "Dec": "dec",                  # Declination                   (Epoch J2000)
            "L": "longitude",              # Galactic longitude            (Degrees)
            "B": "latitude",               # Galactic latitude             (Degrees)
            "R_Sun": "dist_from_sun",      # Distance from the Sun         (kpc)
            "R_Gal": "dist_from_gal_cen",  # Distance from Galactic Center (kpc)
            "X": "X",                      # Galactic distance component X (kpc)
            "Y": "Y",                      # Galactic distance component Y (kpc)
            "Z": "Z",                      # Galactic distance component Z (kpc)

            # Orbital parameters
            # "R_peri": "",                  # Pericentre radius             (kpc)
            #   --> Not available in Harris 1996, 2010 ed.
            # "R_apo": "",                   # Apocentre radius              (kpc)
            #   --> Not available in Harris 1996, 2010 ed.
            # "ecc": "",                     # Orbital eccentricity
            #   --> Not available in Harris 1996, 2010 ed.
            # "phase": "",                   # Orbital phase (1=apo; 0=peri)
            #   --> Not available in Harris 1996, 2010 ed.

            # Metallicity
            "[Fe/H]": "metallicity",      # Metallicity [Fe/H]
            # "": "w_mean_met",           # Weight of mean metallicity
            #   --> Don't know where to stick it in SupaHarris
            # "[Mg/Fe]": "",              # Magnesium abundance
            #   --> Not available in Harris 1996, 2010 ed.
            # "[a/Fe]": "",              # Alpha-element abundance
            #   --> Not available in Harris 1996, 2010 ed.

            # Photometry
            "E(B-V)": "eb_v",             # Foreground reddening, E(B-V)
            "V_HB": "v_hb",               # V magnitude level of the HB, V_HB
            "(m-M)V": "app_vd_mod",       # Apparent visual distance modulus, (m-M)V
            "V_t": "v_t",                 # Integrated V magnitude, V_t
            "M_V,t": "m_v_t",             # Cluster luminosity, M_V,t = V_t - (m-M)V
            "U-B": "ph_u_b",              # U-B
            "B-V": "ph_b_v",              # B-V
            "V-R": "ph_v_r",              # V-R
            "V-i": "ph_v_i",              # V-i
            "spt": "spt",                 # Spectral Type
            "ellip": "ellipticity",       # Projected ellipticity of isophotes, e = 1-(b/a)

            # Velocities
            "v_r": "v_r",                 # Heliocentric radial velocity   (km/s)
            "c_LSR": "c_LSR",             # Radial velocity relative to solar neighbourhood
            # "pmRA": "",                   # RA proper motion
            #   --> Not available in Harris 1996, 2010 ed.
            # "pmDec": "",                  # Dec proper motion
            #   --> Not available in Harris 1996, 2010 ed.
            "sig_v_r": "sig_v",           # Central velocity dispersion (km/s)

            # Structural parameters
            "sp_c"    : "sp_c",          # King concentration parameter
            "sp_r_c"  : "sp_r_c",        # King core radius (arcmin)
            "sp_r_h"  : "sp_r_h",        # Half-light radius (arcmin)
            "sp_mu_V" : "sp_mu_V",       # Central surface brightness (V magnitudes per arcsec^2)
            "sp_rho_0": "rho_0",         # Central luminosity density log10(solar_lum/pc^3)
            "sp_lg_tc": "sp_lg_tc",      # Core relaxation time t(r_c) in log10(yr)
            "sp_lg_th": "sp_lg_th",      # Mean relaxation time t(r_h) in log10(yr)
            # "sp_R_J " : "",              # Jacobii radius
            #   --> not available in Harris 1996, 2010 ed.

            # "Age": "",                     # Age(-estimate) of the GC       (Gyr)
            #   --> not available in Harris 1996, 2010 ed.
            # "Mass": "",                    # Present-day mass               (MSun)
            #   --> not available in Harris 1996, 2010 ed.
            # "Mass_i": "",                  # Initial mass                   (MSun)
            #   --> not available in Harris 1996, 2010 ed.
        })

        print("\nInserting into database :")
        nClusters = len(cluster_list)
        for i, harris in enumerate(cluster_list.values()):
            print("Inserting AstroObject {0} / {1}".format(i+1, nClusters))

            cluster, created = AstroObject.objects.get_or_create(
                name=harris.gid, altname=harris.name,
            )
            cluster.classifications.add(GC)
            cluster.save()
            print("  {0}, created = {1}".format(cluster, created))

            for k, v in parameter_map.items():
                parameter = Parameter.objects.filter(name=k).first()
                if not parameter:
                    print("ERROR: Parameter instance unknown, please add or correct {0}".format(k))
                    import sys; sys.exit(0)

                print("  {0} (Harris) --> {1} (SupaHarris)".format(v, parameter.name))
                value = getattr(harris, v)
                if v in ["v_r", "sig_v"]:
                    sigma_up = getattr(harris, v + "_err")
                    sigma_down = getattr(harris, v + "_err")
                else:
                    sigma_up = None
                    sigma_down = None
                print("  value = {0}".format(value))
                print("  sigma_up = {0}".format(sigma_up))
                print("  sigma_down = {0}".format(sigma_down))

                observation, created = Observation.objects.get_or_create(
                    astro_object=cluster, reference=harris1996ed2010, parameter=parameter,
                    value=value, sigma_up=sigma_up, sigma_down=sigma_down
                )
                print("  {0}, created = {1}\n".format(observation, created))
                # do_continue = input()
            print("")
