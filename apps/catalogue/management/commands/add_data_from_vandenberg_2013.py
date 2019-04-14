#-*- coding: utf-8 -*-

import os
import sys
from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from catalogue.models import Reference
from catalogue.models import Parameter
from catalogue.models import Observation
from catalogue.models import GlobularCluster

from data.parse_vandenberg_2013 import parse_data


class Command(BaseCommand):
    help = "Add VandenBerg (2013) data to the database"

    def handle(self, *args, **options):

        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        ads_url = "https://arxiv.org/abs/1308.2257"
        vandenberg_2013, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}".format(vandenberg_2013))
        else:
            print("Created the Reference: {0}".format(vandenberg_2013))

        cluster_list = parse_data()

        vandenberg_2013

        parameter_map = OrderedDict({
            "NGC": "",
            "Name": "",
            "FeH": "[Fe/H]",
            "Age": "Age",
            "fAge": "",
            "Method": "",
            "Fig": "",
            "Range": "",
            "HBType": "",
            "R_GC": "",
            "M_V": "",
            "v_e,0": "",
            "log10sigma0": ""
        })

        print("\nInserting into database :")
        nClusters = len(cluster_list)
        for i, harris in enumerate(cluster_list.values()):
            print("Inserting GlobularCluster {0} / {1}".format(i+1, nClusters))

            cluster, created = GlobularCluster.objects.get_or_create(
                name=harris.gid, altname=harris.name,
            )
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
                    cluster=cluster, reference=vandenberg_2013, parameter=parameter,
                    value=value, sigma_up=sigma_up, sigma_down=sigma_down
                )
                print("  {0}, created = {1}\n".format(observation, created))
                # do_continue = input()
            print("")
