#-*- coding: utf-8 -*-
import os
import sys
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
from catalogue.utils import map_names_to_ids
from catalogue.utils import PrepareSupaHarrisDatabaseMixin
from data.parse_balbinot_2018 import parse_balbinot_2018


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Balbinot & Gieles (2018) data to the database"

    def handle(self, *args, **options):
        super().handle(print_info=True, *args, **options)  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        self.logger.info("\n\nRunning the management command '{0}'\n".format(cmd))

        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        ads_url = "https://ui.adsabs.harvard.edu/abs/2018MNRAS.474.2479B"
        reference, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            self.logger.info("Found the Reference: {0}\n".format(reference))
        else:
            self.logger.info("Created the Reference: {0}\n".format(reference))

        # We would like to match against the name of an object for many
        # possible variations. The name_id_map contains variations in hopes
        # of catching the existing AstroObject even if the name differs slightly,
        # e.g. Palomar 1/Palomar1/Pal 1/Pal1, etc.
        name_id_map = map_names_to_ids()

        database = parse_balbinot_2018(self.logger)
        for entry in database:
            gc_name = entry[0]
            self.logger.info("gc_name: {0}".format(gc_name))
            continue

            # The Globular Cluster for which you would like to add new data could
            # very well already be known in the database. In that case you should
            # retrieve the AstroObject, and add an Observation
            # to add may
            if gc_name in name_id_map:
                gc = AstroObject.objects.get(id=name_id_map[gc_name])
                logger.info("Found: {0}{1} for '{2}'".format(gc.name,
                    " ({0})".format(gc.altname) if gc.altname else "", gc_name))
                created = False
            else:
                gc, created = AstroObject.objects.get_or_create(name=gc_name)
                gc.classifications.add(self.GC)
                self.logger.info("Created the AstroObject: {0}".format(gc))

            # self.GC is set in PrepareSupaHarrisDatabaseMixin. If another
            # classification, or multiple classifications apply, use e.g.
            # YMC = AstroObjectClassification.objects.get(name="Young Massive Cluster")
            # gc.classifications.add(YMC)
            gc.classifications.add(self.GC)
            gc.save()

            observation = Observation.objects.create(
                reference=reference,
                astro_object=gc,
                parameter=R_Sun,
                value=gc_R_Sun,
            )
            self.logger.info("Created the Observation: {0}".format(observation))
