#-*- coding: utf-8 -*-
import os
import sys
import numpy
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
        BG18, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            self.logger.info("Found the Reference: {0}\n".format(BG18))
        else:
            self.logger.info("Created the Reference: {0}\n".format(BG18))

        # We would like to match against the name of an object for many
        # possible variations. The name_id_map contains variations in hopes
        # of catching the existing AstroObject even if the name differs slightly,
        # e.g. Palomar 1/Palomar1/Pal 1/Pal1, etc.
        name_id_map = map_names_to_ids()

        # Create missing Parameter instances, and set up parameter map
        mu, created = Parameter.objects.get_or_create(
            name="mu", description="Remaining mass fraction of cluster",
            scale=1.0
        )
        if not created:
            self.logger.info("Found the Parameter: {0}\n".format(mu))
        else:
            self.logger.info("Created the Parameter: {0}\n".format(mu))
        parameter_map = {
            # Compiled by B&G18 from various sources, see pm_reference_map
            "mu_alpha": Parameter.objects.get(name="pmRA"),
            "mu_delta": Parameter.objects.get(name="pmDec"),

            # B&G18: Line-of-sight velocity; SupaHarris: Heliocentric radial velocity
            # The first five entries are exactly the values in Harris (1996),
            # so no need to insert B&G18 v_los into SupaHarris
            # "V_rm los": Parameter.objects.get(name="v_r"),

            # B&G initialise 1500 Orbit instances in Galpy's MWPotential2014
            # (Bovy 2015) to take into account observational uncertainties
            # and present the median /w median absolute deviation as uncertainty
            "R_apo": Parameter.objects.get(name="R_apo"),
            "R_peri": Parameter.objects.get(name="R_peri"),
            "ecc": Parameter.objects.get(name="ecc"),
            "M_i": Parameter.objects.get(name="Mass_i"),
            "mu": Parameter.objects.get(name="mu"),
            # B&G18 define phase as (R_G - R_peri) / (R_apo - R_peri), which
            # equals 0 for R_G=R_peri and 1 for R_G=R_apo. This is consistent
            # with the definition of phase in SupaHarris database.
            "phi": Parameter.objects.get(name="phase"),
            "r_J": Parameter.objects.get(name="sp_R_J"),
        }

        # See Balbinot & Gieles (2018) Table 1.
        pm_reference_map = {
             1: "1997AJ....114.1014D",
             2: "1999AJ....117..277D",
             3: "1999AJ....117.1792D",
             4: "2003AJ....125.1373D",
             5: "2007AJ....134..195C",
             6: "2010AJ....140.1282C",
             7: "2013AJ....146...33C",
             8: "2006A&AT...25..185D",
             9: "2015ApJ...803...80K",
            10: "2015MNRAS.450.3270R",
            11: "1996MNRAS.278..251S",
        }
        for bibcode in pm_reference_map.values():
            ads_url = "https://ui.adsabs.harvard.edu/abs/{0}".format(bibcode)
            reference, created = Reference.objects.get_or_create(ads_url=ads_url)
            if not created:
                self.logger.info("Found the Reference: {0}\n".format(reference))
            else:
                self.logger.info("Created the Reference: {0}\n".format(reference))

        # Finally - with all info in database in place - add B&G18 to SupaHarris
        database = parse_balbinot_2018(self.logger)

        # First we add the proper motions b/c Reference != B&G18
        has_pm, = numpy.where(
            numpy.isfinite(database["mu_alpha"])
            & numpy.isfinite(database["mu_delta"])
        )
        Nentries = len(has_pm)
        for i, entry in enumerate(database[has_pm]):
            self.logger.debug("\nAdding pm {0}/{1} to database".format(i+1, Nentries))
            self.logger.debug("  {0}".format(entry))

            self.logger.debug("  {0}, {1}, {2}".format(
                entry["mu_alpha"], entry["mu_delta"], entry["Refs"]
            ))

            gc_name = entry["Name"]
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            self.logger.debug("  astro_object: {0}".format(gc))

            refs = entry["Refs"]
            self.logger.debug("  refs: {0}".format(refs))
            if "," in refs:
                self.logger.warning("  WARNING: {0} has multiple pm refs\n    {1}".format(
                    gc_name, "\n    ".join(pm_reference_map[int(r)] for r in refs.split(",")))
                )
                first_ref = pm_reference_map[int(refs.split(",")[0])]
                first_ref = Reference.objects.get(bib_code=first_ref)
            elif refs == "nan":
                self.logger.warning("  WARNING: {0} has no Refs. Using BG18".format(gc_name))
                first_ref = BG18

            else:
                first_ref = pm_reference_map[int(float(refs))]
                first_ref = Reference.objects.get(bib_code=first_ref)
            self.logger.info("  reference: {0}".format(first_ref))

            for param in ["mu_alpha", "mu_delta"]:
                obs, created = Observation.objects.get_or_create(
                    astro_object=gc,
                    parameter=parameter_map[param],
                    reference=first_ref,  # TODO: add support for multiple References?
                    value=entry[param],
                    sigma_up=entry[param+"_err"], sigma_down=entry[param+"_err"]
                )
                if not created:
                    self.logger.info("  Found the Observation: {0}".format(obs))
                else:
                    self.logger.info("  Created the Observation: {0}".format(obs))

        # Second we add R_peri, R_apo, eccentricity, phase, initial mass, mass loss
        Nentries = len(database)
        for i, entry in enumerate(database):
            self.logger.debug("\nAdding {0}/{1} to database".format(i+1, Nentries))
            self.logger.debug("  {0}".format(entry))

            self.logger.debug("  {0}, {1}, {2}".format(
                entry["mu_alpha"], entry["mu_delta"], entry["Refs"]
            ))

            gc_name = entry["Name"]
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            self.logger.debug("  astro_object: {0}".format(gc))

            for param in ["R_apo", "R_peri", "ecc", "phi", "M_i", "mu"]:
                obs, created = Observation.objects.get_or_create(
                    astro_object=gc,
                    parameter=parameter_map[param],
                    reference=BG18,
                    value=entry[param],
                    sigma_up=entry[param+"_err"], sigma_down=entry[param+"_err"]
                )
                if not created:
                    self.logger.info("  Found the Observation: {0}".format(obs))
                else:
                    self.logger.info("  Created the Observation: {0}".format(obs))
