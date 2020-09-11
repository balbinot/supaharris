# -*- coding: utf-8 -*-
import os
import sys

import numpy
from catalogue.models import (
    AstroObject,
    AstroObjectClassification,
    Observation,
    Parameter,
    Profile,
    Reference,
)
from catalogue.utils import PrepareSupaHarrisDatabaseMixin
from data.parse_trager_1995 import parse_trager_1995_gc, parse_trager_1995_tables
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def add_trager_1995_table2(logger, table2):
    # Trager+ 1995 Table 2 does not seem to be available in machine-readable form.
    trager1995 = Reference.objects.get(bib_code="1995AJ....109..218T")
    logger.debug("\nInsert Trager (1995) Table 2")

    return


def add_trager_1995_profiles(logger, gc, tables):
    trager1995 = Reference.objects.get(bib_code="1995AJ....109..218T")
    logger.debug("\nInsert Trager (1995) profiles")

    # We first delete all Profile instances that match deBoer19 Reference
    deleted = Profile.objects.filter(reference=trager1995).delete()
    if deleted[0] is not 0:
        logger.debug("WARNING: deleted {0} Profile instances".format(deleted))

    Nentries = len(gc)
    for i, gc_name in enumerate(gc["Name"]):
        logger.debug("\n{0}/{1}: {2}".format(i + 1, Nentries, gc_name))
        ao = AstroObject.objects.filter(name=gc_name).first()
        if ao:
            logger.info("  Found the AstroObject: {0}".format(ao))
        else:
            logger.info("  Did not find AstroObject")
            void = input("ERROR. Press any key to continue")

        (igc,) = numpy.where(tables["Name"] == gc_name)
        logger.debug("  Profile has {} entries".format(len(tables[igc])))

        ikeep = Ellipsis
        if gc_name == "NGC 2419":  # the data shows two radial profiles
            (ikeep,) = numpy.where(
                (tables[igc]["DataSet"] != "CGB1")
                & (tables[igc]["DataSet"] != "CGB2")
                & (tables[igc]["DataSet"] != "CGR1")
                & (tables[igc]["DataSet"] != "CGR2")
                & (tables[igc]["DataSet"] != "CGV2")
                & (tables[igc]["DataSet"] != "CGV1")
                & (tables[igc]["DataSet"] != "CGV3")
            )

        sh_prof = Profile(
            reference=trager1995,
            astro_object=ao,
            x=tables[igc]["logr"][ikeep].tolist(),
            y=tables[igc]["muV"][ikeep].tolist(),
            x_description="logr: Log of radius of surface brightness [arcsec]",
            y_description="mu_V(r): surface brightness at r in V mags [mag/arcsec**2]",
        )
        sh_prof.save()

        # TODO: if needed: can also add tables[igc]["muVf"][ikeep], which
        # shows Trager+1995's Chebyshev fit /w units mag/arcsec^2, and/or
        # its residuals tables[igc]["Resid"][ikeep] /w units mag/arcsec^2


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Trager+ (1995) data to the database"

    def handle(self, *args, **options):
        super().handle(*args, **options)  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        self.logger.info("\n\nRunning the management command '{0}'\n".format(cmd))

        ads_url = "https://ui.adsabs.harvard.edu/abs/1995AJ....109..218T"
        reference, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            self.logger.info("Found the Reference: {0}\n".format(reference))
        else:
            self.logger.info("Created the Reference: {0}\n".format(reference))

        gc = parse_trager_1995_gc(self.logger)
        tables = parse_trager_1995_tables(self.logger)

        # add_trager_1995_table2(self.logger, table2)
        add_trager_1995_profiles(self.logger, gc, tables)
