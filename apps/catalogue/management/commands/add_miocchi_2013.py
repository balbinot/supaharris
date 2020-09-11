# -*- coding: utf-8 -*-
import os
import sys

from catalogue.models import (
    AstroObject,
    AstroObjectClassification,
    Observation,
    Parameter,
    Profile,
    Reference,
)
from catalogue.utils import PrepareSupaHarrisDatabaseMixin, map_names_to_ids
from data.parse_miocchi_2013 import (
    parse_miocchi_2013_profiles,
    parse_miocchi_2013_table2,
)
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def add_miocchi_2013_table2(logger):
    miocchi13 = Reference.objects.get(bib_code="2013ApJ...774..151M")
    logger.debug("\nInsert Miocchi+ (2013) Table 2")

    # We first delete all Observation instances that match miocchi13 Reference
    deleted = Observation.objects.filter(reference=miocchi13).delete()
    if deleted[0] != 0:
        logger.debug("WARNING: deleted {0} Profile instances".format(deleted))

    name_id_map = map_names_to_ids()

    logger.debug("\nChecking/creating required parameters")
    parameter_map = {
        "NGCno.": "bla",
        "mod": "bla",
        "W0": "bla",
        "+dW0": "bla",
        "-dW0": "bla",
        "rc": "bla",
        "+drc": "bla",
        "-drc": "bla",
        "r0": "bla",
        "+dr0": "bla",
        "-dr0": "bla",
        "c0": "bla",
        "+dc0": "bla",
        "-dc0": "bla",
        "rl": "bla",
        "+drl": "bla",
        "-drl": "bla",
        "rhm": "bla",
        "+drhm": "bla",
        "-drhm": "bla",
        "re": "bla",
        "+dre": "bla",
        "-dre": "bla",
        "N_BG": "bla",
        "chi2_nu": "bla",
    }

    database = parse_miocchi_2013_table2(logger)
    Nentries = len(database)
    for i, entry in enumerate(database):
        gc_name = entry[0]
        logger.info("{0}/{1}: {2}".format(i + 1, Nentries, gc_name))
        gc = AstroObject.objects.get(id=name_id_map[gc_name])

        if entry["mod"] == "W":
            model = "Wilson"
        elif entry["mod"] == "K":
            model = "King"
        else:
            logger.error("ERROR: model is {} but expected W/K".format(entry["mod"]))
            break

        logger.info("Model: {0}\n".format(model))
        continue

        observation = Observation.objects.create(
            reference=reference, astro_object=gc, parameter=R_Sun, value=gc_R_Sun,
        )
        logger.info("Created the Observation: {0}".format(observation))


def add_miocchi_2013_profiles(logger):
    miocchi13 = Reference.objects.get(bib_code="2013ApJ...774..151M")
    logger.debug("\nInsert Miocchi+ (2013) star count profiles")

    # We first delete all Profile instances that match miocchi13 Reference
    deleted = Profile.objects.filter(reference=miocchi13).delete()
    if deleted[0] != 0:
        logger.debug("WARNING: deleted {0} Profile instances".format(deleted))

    m13_profs = parse_miocchi_2013_profiles(logger)
    Nprofiles = len(m13_profs)
    for i, (gc_name, profile) in enumerate(m13_profs.items()):
        gc = AstroObject.objects.get(name=gc_name)
        logger.debug("\n{0}/{1}: {2}".format(i + 1, Nprofiles, gc))
        sh_prof = Profile(
            reference=miocchi13,
            astro_object=gc,
            x=list(profile["radius"]),
            y=list(profile["log_surface_density"]),
            y_sigma_up=list(profile["err_log_surface_density"]),
            y_sigma_down=list(profile["err_log_surface_density"]),
            x_description="logr: Log of radius [arcsec]",
            y_description="log Sigma_*(r): Log of decontaminated projected"
            + " star count [1/arcsec**2]",
        )
        sh_prof.save()


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Miocchi+ (2013) data to the database"

    def handle(self, *args, **options):
        super().handle(
            print_info=True, *args, **options
        )  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        self.logger.info("\n\nRunning the management command '{0}'\n".format(cmd))

        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        ads_url = "https://ui.adsabs.harvard.edu/abs/2013ApJ...774..151M"
        reference, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            self.logger.info("Found the Reference: {0}\n".format(reference))
        else:
            self.logger.info("Created the Reference: {0}\n".format(reference))

        add_miocchi_2013_table2(self.logger)
        add_miocchi_2013_profiles(self.logger)
