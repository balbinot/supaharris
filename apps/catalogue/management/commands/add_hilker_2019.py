#-*- coding: utf-8 -*-
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models import (
    Reference,
    Parameter,
    Observation,
    AstroObject,
    AstroObjectClassification,
)
from catalogue.utils import PrepareSupaHarrisDatabaseMixin
from data.parse_hilker_2019 import (
    parse_hilker_2019_orbits,
    parse_hilker_2019_combined,
    parse_hilker_2019_radial_velocities,
)


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Hilker+ 2019 data to the SupaHarris database"

    def handle(self, *args, **options):
        super().handle(print_info=True, *args, **options)  # to run our Mixin modifications
        return

        cmd = __file__.split("/")[-1].replace(".py", "")
        print("\n\nRunning the management command '{0}'\n".format(cmd))

        # Copy-paste from arXiv:1908.02778v1:
        # Baumgardt (2017) first compared a large grid of 900 N-body models to
        # the velocity dispersion and surface brightness profiles of 50 GGCs
        # in order to determine their masses and mass-to-light ratios.
        #
        # Baumgardt 2017, https://arxiv.org/pdf/1609.08794.pdf
        # http://simbad.u-strasbg.fr/simbad/sim-ref?querymethod=bib&simbo=on&submit=submit+bibcode&bibcode=2017MNRAS.464.2174B
        ads_url = "https://ui.adsabs.harvard.edu/abs/2017MNRAS.464.2174B"
        baumgardt2017, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(baumgardt2017))
        else:
            print("Created the Reference: {0}\n".format(baumgardt2017))

        # Copy-paste from arXiv:1908.02778v1:
        # Additionally, Sollima & Baumgardt (2017) presented the global mass
        # functions of 35 GGCs based on deep HST photometry in combination
        # with multimass dynamical models.
        #
        # Sollima & Baumgardt (2017), https://arxiv.org/pdf/1708.09529.pdf
        ads_url = "https://ui.adsabs.harvard.edu/abs/2017MNRAS.471.3668S"
        sollima_baumgardt_2017, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(sollima_baumgardt_2017))
        else:
            print("Created the Reference: {0}\n".format(sollima_baumgardt_2017))

        # Copy-paste from arXiv:1908.02778v1:
        # One year later, Baumgardt & Hilker (2018) deter- mined masses, stellar
        # mass functions, and structural parameters of 112 GGCs by fitting a
        # large set of N-body simulations to their velocity dispersion and surface
        # density profiles.
        #
        # Baumgardt & Hilker 2018, https://arxiv.org/pdf/1804.08359.pdf
        ads_url = "https://ui.adsabs.harvard.edu/abs/2018MNRAS.478.1520B"
        Baumgardt_Hilker_2018, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(Baumgardt_Hilker_2018))
        else:
            print("Created the Reference: {0}\n".format(Baumgardt_Hilker_2018))

        # Copy-paste from arXiv:1908.02778v1:
        # When Gaia DR2 became public, Baumgardt et al. (2019) presented mean
        # proper motions and space velocities of 154 GGCs and the velocity
        # dispersion profiles of 141 globular clusters based on a combination
        # of Gaia DR2 proper motions with ground-based line-of-sight velocities.
        # The combination of these velocity dispersion profiles with new
        # measurements of the internal mass functions allowed to model the internal
        # kinematics of 144 GGCs, more than 90 per cent of the currently known
        # Milky Way globular cluster population
        #
        # Baumgardt, Hilker, Sollima & Bellini 2019, https://arxiv.org/pdf/1811.01507.pdf
        ads_url = "https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B"
        BHSB2019, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(BHSB2019))
        else:
            print("Created the Reference: {0}\n".format(BHSB2019))
        # J/MNRAS/482/5138/table1
        # J/MNRAS/482/5138/table4

        # Finally, Sollima, Baumgardt & Hilker (2019) analysed the internal
        # kinematics of 62 GGCs, finding significant rotation in 15 of them.
        # https://arxiv.org/pdf/1902.05895.pdf
        ads_url = "https://ui.adsabs.harvard.edu/abs/2019MNRAS.485.1460S"
        SBH2019, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(SBH2019))
        else:
            print("Created the Reference: {0}\n".format(SBH2019))

        hilker_2019_orbits = parse_hilker_2019_orbits()
        hilker_2019_combined = parse_hilker_2019_combined()
        hilker_2019_radial_velocities = parse_hilker_2019_radial_velocities()
