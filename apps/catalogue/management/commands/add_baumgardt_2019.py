#-*- coding: utf-8 -*-
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from astroquery.vizier import Vizier
Vizier.ROW_LIMIT = -1

from catalogue.models import (
    Reference,
    Parameter,
    Observation,
    AstroObject,
    AstroObjectClassification,
)
from catalogue.utils import PrepareSupaHarrisDatabaseMixin


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Baumgardt+ 2019, table 1 to the SupaHarris database"

    def handle(self, *args, **options):
        super().handle(print_info=True, *args, **options)  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        print("\n\nRunning the management command '{0}'\n".format(cmd))

        # Baumgardt, Hilker, Sollima & Bellini 2019, https://arxiv.org/pdf/1811.01507.pdf
        # J/MNRAS/482/5138/table1 <---
        # J/MNRAS/482/5138/table4
        ads_url = "https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B"
        BHSB2019, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(BHSB2019))
        else:
            print("Created the Reference: {0}\n".format(BHSB2019))

        data = Vizier.get_catalogs('J/MNRAS/482/5138/table1')[0]

        # For IC 1257 and Ter 10 we found that the cluster centres given in Harris (1996)
        # were incorrect, and determined new centres for the positions of the member
        # stars found in the Gaia DR2 catalogue.

        # This work measured (mean) proper motions and line of sight velocities and
        # errors for GCs in the Milky Way. Moreover, the authors calculated the
        # internal velocity dispersion profiles.

        for p_b19 in data.keys():
            print("p_b19: {0}".format(p_b19))

        for entry in data:
            entry["Name"]

