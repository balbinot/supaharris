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
from catalogue.management.commands.add_author_year import (
    PrepareSupaHarrisDatabaseMixin)

from data.parse_vandenberg_2013 import read_vandenberg2013_data


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add VandenBerg (2013) data to the database"

    def handle(self, *args, **options):
        super().handle(*args, **options)  # to inherit the parent modifications

        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        # ads_url = "https://arxiv.org/abs/1308.2257"
        ads_url = "https://ui.adsabs.harvard.edu/abs/2013ApJ...775..134V"
        vandenberg_2013, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("\nFound the Reference: {0}".format(vandenberg_2013))
        else:
            print("\nCreated the Reference: {0}".format(vandenberg_2013))

        data = read_vandenberg2013_data()

        # Keys: Values --> SupaHarris: VandenBerg parameter names
        parameter_map = OrderedDict({
            # Used for identifying the object; not added as Observation
            # "NGC": "",
            # "Name": "",

            # the third column lists the adopted [Fe/H] values from the study
            # by CBG09 (or, in the case of Terzan 8, from Mottini+ 2008).
            # "[Fe/H]": "[Fe/H]",

            "Age": "Age",
            # "fAge": "",
            # "Method": "",
            # "Fig": "",
            # "Range": "",

            # HB type (from Mackey & van den Bergh 2005)
            # "HBType": "",

            # both R_G and M_V have been taken from the 2010 edition of
            # the catalog by Harris 1996),
            # "R_GC": "",  # Galactocentric distance in kpc
            # "M_V": "",  # absolute integrated visual magnitude

            # The calculation is described in Sec. 6.2
            "v_e_0": "v_e0",  # Central escape velocity
            # surface density of stars at the cluster center
            "sigma_0": "sigma0"
        })

        v_e_0 = Parameter.objects.filter(name="v_e_0").first()
        if not v_e_0:
            v_e_0 = Parameter(name="v_e_0")
            v_e_0.description = "Central escape velocity"
            v_e_0.unit = "km/s"
            v_e_0.scale = 1.0
            v_e_0.save()
            print("\nCreated the Parameter: {0}".format(v_e_0))
        else:
            print("\nFound the Parameter: {0}".format(v_e_0))

        sigma_0 = Parameter.objects.filter(name="sigma_0").first()
        if not sigma_0:
            sigma_0 = Parameter(name="sigma_0")
            sigma_0.description = "Central surface density of stars at the cluster center"
            sigma_0.unit = "MSun/pc^2"
            sigma_0.scale = 1
            sigma_0.save()
            print("Created the Parameter: {0}".format(sigma_0))
        else:
            print("Found the Parameter: {0}".format(sigma_0))

        print(data.dtype)

        print("\nInserting into database :")
        nClusters = len(data)
        for i, cluster in enumerate(data):
            print("\nAstroObject {0} / {1}".format(i+1, nClusters))

            name = "NGC {0}".format(cluster["NGC"])
            altname = None
            if cluster["Name"]:
                clustername = cluster["Name"].decode("utf-8").replace(
                    "M", "M ").replace("Arp", "Arp ").replace(
                    "Pal", "Pal ").replace("Ter", "Terzan ").replace("Tuc", " Tuc")
            else:
                clustername = None
            if name == "NGC -1":
                name = clustername
            else:
                altname = clustername

            print("  name: {0}".format(name))
            print("  altname: {0}".format(altname))
            cluster, created = AstroObject.objects.get_or_create(
                name=name
            )
            print("  {0}, created = {1}".format(cluster, created))
            if created:
                cluster.classifications.add(GC)
                cluster.save()

            for k, v in parameter_map.items():
                parameter = Parameter.objects.filter(name=k).first()
                if not parameter:
                    print("ERROR: Parameter instance unknown, please add or correct {0}".format(k))
                    import sys; sys.exit(0)

                print("  {0} (vandenBerg) --> {1} (SupaHarris)".format(v, parameter.name))
                value = data[v][i]
                if v in ["Age"]:
                    sigma_up = data["fAge"][i]
                    sigma_down = data["fAge"][i]
                else:
                    sigma_up = None
                    sigma_down = None
                print("    value = {0}".format(value))
                print("    sigma_up = {0}".format(sigma_up))
                print("    sigma_down = {0}".format(sigma_down))

                observation, created = Observation.objects.get_or_create(
                    astro_object=cluster, reference=vandenberg_2013, parameter=parameter,
                    value=value, sigma_up=sigma_up, sigma_down=sigma_down
                )
                print("  {0}, created = {1}\n".format(observation, created))
                # do_continue = input()
            print("")
