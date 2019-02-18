#-*- coding: utf-8 -*-
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from catalogue.models import Reference
from catalogue.models import Parameter
from catalogue.models import Observation
from catalogue.models import GlobularCluster
from catalogue.utils import get_parameter_names_from_supaharris

from data.parse_AuthorYear.py import parse_data


class Command(BaseCommand):
    help = "Add ReplaceMe data to the database"

    def handle(self, *args, **options):
        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        ads_url = "http://adsabs.harvard.edu/abs/1996AJ....112.1487H"
        harris1996ed2010, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}".format(harris1996ed2010))
        else:
            print("Created the Reference: {0}".format(harris1996ed2010))

        # Make sure that you convert the parameters available in your database
        # to the parameters available in the SupaHarris database. This function
        # below will print all parameters for you.
        get_parameter_names_from_supaharris()

        # Here we get one particular parameter as an example to help you
        # See https://docs.djangoproject.com/en/2.1/topics/db/queries/
        # for an explanation of how to retrieve/create items from/in the database.
        R_Sun = Parameter.objects.filter(name="R_Sun").first()
        if R_Sun:
            print("The parameter is available: R_Sun.name = {0}".format(R_Sun.name))
        else:
            print("The parameter is not available. It may be needed to create it")
            # See apps/catalogue/models.py for the definition and requirements of Parameter
            R_Sun = Parameter.objects.create(
                name="R_Sun",  # must be a string, max 64 characters
                description="Distance to the Sun",  # must be a string, max. 256 characters
                unit="kpc",  # must be a string, max 63 characters. Note that the unit must comply with astropy.unit.
                scale=3.0  # must be a float. This is the scale by which parameters must be multiplied by.
            )

        database = parse_data(save_to_xlsx=False)  # save_to_xlsx requires openpyxl
        for entry in database:
            gc_name = entry[0]
            gc_R_Sun = entry[1]

            print("gc_name: {0}".format(gc_name))
            print("gc_R_Sun: {0}".format(gc_R_Sun))

            # The Globular Cluster for which you would like to add new data could
            # very well already be known in the database. In that case you should
            # retrieve the GlobularCluster, and add an Observation
            # to add may
            gc, created = GlobularCluster.objects.get_or_create(name=gc_name)
            if not created:
                print("Found the GlobularCluster: {0}".format(gc))
            else:
                print("Created the GlobularCluster: {0}".format(gc))

            # TODO
            gc.save()

