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
from catalogue.utils import PrepareSupaHarrisDatabaseMixin
from data.parse_author_year import parse_author_year_data


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add ReplaceMe data to the database"

    def handle(self, *args, **options):
        logger = logging.getLogger("console")
        super().handle(print_info=True, *args, **options)  # to run our Mixin modifications
        return

        cmd = __file__.split("/")[-1].replace(".py", "")
        print("\n\nRunning the management command '{0}'\n".format(cmd))

        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        ads_url = "https://ui.adsabs.harvard.edu/abs/1996AJ....112.1487H"
        reference, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(reference))
        else:
            print("Created the Reference: {0}\n".format(reference))

        # Here we get one particular parameter as an example to help you
        # See https://docs.djangoproject.com/en/2.2/topics/db/queries/
        # for an explanation of how to retrieve/create items from/in the database.
        R_Sun = Parameter.objects.filter(name="R_Sun").first()
        if R_Sun:
            print("\nThe parameter is available: R_Sun.name = {0}".format(R_Sun.name))
        else:
            print("\nThe parameter is not available. It may be needed to create it")
            # See apps/catalogue/models.py for the definition and requirements of Parameter
            R_Sun = Parameter.objects.create(
                name="R_Sun",  # must be a string, max 64 characters
                description="Distance to the Sun",  # must be a string, max. 256 characters
                unit="kpc",  # must be a string, max 63 characters. Note that the unit must comply with astropy.unit.
                scale=1.0  # must be a float. This is the scale by which parameters must be multiplied by.
            )

        database = parse_author_year_data()
        for entry in database:
            gc_name = entry[0]
            gc_R_Sun = entry[1]

            print("gc_name: {0}".format(gc_name))
            print("gc_R_Sun: {0}".format(gc_R_Sun))

            # The Globular Cluster for which you would like to add new data could
            # very well already be known in the database. In that case you should
            # retrieve the AstroObject, and add an Observation
            # to add may
            gc, created = AstroObject.objects.get_or_create(name=gc_name)
            if not created:
                print("Found the AstroObject: {0}".format(gc))
            else:
                print("Created the AstroObject: {0}".format(gc))

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
            print("Created the Observation: {0}".format(observation))
