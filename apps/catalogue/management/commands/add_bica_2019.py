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
from data.parse_bica_2019 import (
    parse_bica_2019_refs,
    parse_bica_2019_table2,
    parse_bica_2019_table3,
    parse_bica_2019_table4,
    parse_bica_2019_table5,
)


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Bica+ 2019 data to the database"

    def handle(self, *args, **options):
        super().handle(print_info=True, *args, **options)  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        print("\n\nRunning the management command '{0}'\n".format(cmd))

        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        for ref_code, ads_url in zip(
        [
            "bica2019", "REF103", "REF1743", "REF1737", "REF1738",
            "REF3044", "REF508", "REF295", "REF927", "REF213",
        ],
        [
            "https://ui.adsabs.harvard.edu/abs/2019AJ....157...12B",  # primary
            # ... and all additional (nested) references
            "https://ui.adsabs.harvard.edu/abs/1958ApJ...128..259H",  # REF103
            "https://ui.adsabs.harvard.edu/abs/1958MNRAS.118..154E",  # REF1743
            "https://ui.adsabs.harvard.edu/abs/1959Obs....79...88E",  # REF1737
            "https://ui.adsabs.harvard.edu/abs/1959MNRAS.119..278S",  # REF1738
            "https://ui.adsabs.harvard.edu/abs/1959SvA.....3..188M",  # REF3044
            "https://ui.adsabs.harvard.edu/abs/1964ARA&A...2..213B",  # REF508
            "https://ui.adsabs.harvard.edu/abs/1966ArA.....4...65L",  # REF295
            "https://ui.adsabs.harvard.edu/abs/1966AJ.....71..990V",  # REF927
            "https://ui.adsabs.harvard.edu/abs/1967IrAJ....8..126A",  # REF213
        ]):
            reference, created = Reference.objects.get_or_create(ads_url=ads_url)
            setattr(Reference, ref_code, reference)
            if not created:
                print("Found the Reference: {0}\n".format(ref_code))
            else:
                print("Created the Reference: {0}\n".format(ref_code))

        return

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

        bica2019_table2 = parse_bica_2019_table2()
        for entry in data:
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

