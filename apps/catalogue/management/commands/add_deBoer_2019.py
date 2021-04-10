# -*- coding: utf-8 -*-
import glob
import os
import sys

from catalogue.models import (
    AstroObject,
    AstroObjectClassification,
    Auxiliary,
    Observation,
    Parameter,
    Profile,
    Reference,
)
from catalogue.utils import PrepareSupaHarrisDatabaseMixin, map_names_to_ids
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from data.parse_deBoer_2019 import (
    fix_gc_names,
    parse_deBoer_2019_fits,
    parse_deBoer_2019_member_stars,
    parse_deBoer_2019_stitched_profiles,
)

BASEDIR = "/" + __file__.split("/")[1] + "/data/MW_GCS_deBoer2019/"


def add_deBoer_2019_tableB1(logger):
    deBoer19 = Reference.objects.get(bib_code="2019MNRAS.485.4906D")
    logger.debug("\nInsert de Boer (2019) Table B1")
    deBoer_fits = parse_deBoer_2019_fits(logger)
    Nentries = len(deBoer_fits)
    names = deBoer_fits.dtype.names

    # We first delete all Observation instances that match deBoer19 Reference
    deleted = Observation.objects.filter(reference=deBoer19).delete()
    if deleted[0] is not 0:
        logger.debug("WARNING: deleted {0} Observation instances".format(deleted))

    logger.debug("\nChecking/creating required parameters")
    parameter_map = {
        # King
        "W_king": "sp_king_W",
        "rt_king": "sp_king_r_t",
        "M_king": "sp_king_M",
        "kinghalf": "sp_king_r_hm",
        "kingtrunc": "sp_king_r_l",
        "chi2_king": "sp_king_chi2",
        "chi2red_king": "sp_king_chi2red",
        # Wilson
        "W_wil": "sp_wilson_W",
        "rt_wil": "sp_wilson_r_t",
        "M_wil": "sp_wilson_M",
        "wilhalf": "sp_wilson_r_hm",
        "wiltrunc": "sp_wilson_r_l",
        "chi2_wil": "sp_wilson_chi2",
        "chi2red_wil": "sp_wilson_chi2red",
        # Limepy
        "W_lime": "sp_limepy_W",
        "g_lime": "sp_limepy_g",
        "rt_lime": "sp_limepy_r_t",
        "M_lime": "sp_limepy_M",
        "limehalf": "sp_limepy_r_hm",
        "chi2_lime": "sp_limepy_chi2",
        "chi2red_lime": "sp_limepy_chi2red",
        # SPES
        "W_pe": "sp_spes_W",
        "eta_pe": "sp_spes_eta",
        "log1minB_pe": "sp_spes_log1minB",
        "rt_pe": "sp_spes_r_t",
        "M_pe": "sp_spes_M",
        "pecore": "sp_spes_r_c",
        "log_fpe": "sp_spes_log_fpe",
        "pehalf": "sp_spes_r_hm",
        "chi2_pe": "sp_spes_chi2",
        "chi2red_pe": "sp_spes_chi2red",
        "r_tie": "deBoer19_r_tie",
        "BGlev": "deBoer19_BGlev",
        "min_mass": "deBoer19_M_min",
        "max_mass": "deBoer19_M_max",
    }
    parameter_descriptions = {
        "sp_king_W": "King (1966) central potential",
        "sp_king_r_t": "King (1966) tidal radius",
        "sp_king_M": "King (1966) cluster mass",
        "sp_king_r_hm": "King (1966) half-mass radius",
        "sp_king_r_l": "King (1966) limiting/truncation radius",
        "sp_king_chi2": "King (1966) model fit chi2",
        "sp_king_chi2red": "King (1966) model fit chi2red",
        "sp_wilson_W": "Wilson (1975) central potential",
        "sp_wilson_r_t": "Wilson (1975) tidal radius",
        "sp_wilson_M": "Wilson (1975) cluster mass",
        "sp_wilson_r_hm": "Wilson (1975) half-mass radius",
        "sp_wilson_r_l": "Wilson (1975) limiting/truncation radius",
        "sp_wilson_chi2": "Wilson (1975) model fit chi2",
        "sp_wilson_chi2red": "Wilson (1975) model fit chi2red",
        "sp_limepy_W": "Limepy central potential",
        "sp_limepy_g": "Limepy truncation parameter g, see Gieles & Zocchi (2015)",
        "sp_limepy_r_t": "Limepy tidal radius",
        "sp_limepy_M": "Limepy cluster mass",
        "sp_limepy_r_hm": "Limepy half-mass radius",
        "sp_limepy_chi2": "Limepy model fit chi2",
        "sp_limepy_chi2red": "Limepy model fit chi2red",
        "sp_spes_W": "SPES central potential",
        "sp_spes_eta": "SPES eta: ratio of 1D vel. dispersion of PEs over vel. scale s, see Claydon+ 2017,2019",
        "sp_spes_log1minB": "SPES B. B=1 --> no PEs (DF is King DF); 0<=B<=1 model has PEs",
        "sp_spes_r_t": "SPES tidal radius",
        "sp_spes_M": "SPES cluster mass",
        "sp_spes_r_c": "SPES core radius",
        "sp_spes_log_fpe": "SPES fpe is the fraction of PE stars",
        "sp_spes_r_hm": "SPES half-mass radius",
        "sp_spes_chi2": "SPES model fit chi2",
        "sp_spes_chi2red": "SPES model fit chi2red",
        "deBoer19_r_tie": "de Boer (2019) Gaia completeness radius used to tie observations together",
        "deBoer19_BGlev": "de Boer (2019) star count background level",
        "deBoer19_M_min": "de Boer (2019) minimum cluster mass",
        "deBoer19_M_max": "de Boer (2019) maximum cluster mass",
    }
    parameter_units = {
        "sp_king_W": "",
        "sp_king_r_t": "pc",
        "sp_king_M": "Msun",
        "sp_king_r_hm": "pc",
        "sp_king_r_l": "pc",
        "sp_king_chi2": "",
        "sp_king_chi2red": "",
        "sp_wilson_W": "",
        "sp_wilson_r_t": "pc",
        "sp_wilson_M": "Msun",
        "sp_wilson_r_hm": "pc",
        "sp_wilson_r_l": "pc",
        "sp_wilson_chi2": "",
        "sp_wilson_chi2red": "",
        "sp_limepy_W": "",
        "sp_limepy_g": "",
        "sp_limepy_r_t": "pc",
        "sp_limepy_M": "Msun",
        "sp_limepy_r_hm": "pc",
        "sp_limepy_chi2": "",
        "sp_limepy_chi2red": "",
        "sp_spes_W": "",
        "sp_spes_eta": "",
        "sp_spes_log1minB": "",
        "sp_spes_r_t": "pc",
        "sp_spes_M": "Msun",
        "sp_spes_r_c": "pc",
        "sp_spes_log_fpe": "",
        "sp_spes_r_hm": "pc",
        "sp_spes_chi2": "",
        "sp_spes_chi2red": "",
        "deBoer19_r_tie": "arcmin",
        "deBoer19_BGlev": "1 / arcmin^2",
        "deBoer19_M_min": "Msun",
        "deBoer19_M_max": "Msun",
    }
    for sh_parameter in parameter_map.values():
        sh_p, created = Parameter.objects.get_or_create(
            name=sh_parameter,
            unit=parameter_units[sh_parameter],
            description=parameter_descriptions[sh_parameter],
            scale=1.0,
        )
        if not created:
            logger.info("  Found the Parameter: {0}".format(sh_p))
        else:
            logger.info("  Created the Parameter: {0}".format(sh_p))

    logger.debug("\nIterating through all entries in the table")
    all_observations = []
    for i, entry in enumerate(deBoer_fits):
        gc_name = entry["id"]
        gc = AstroObject.objects.get(name=gc_name)
        logger.debug("\ndeBoer2019 fit {0}/{1}: {2}".format(i + 1, Nentries, gc))

        # King (1966): 1966AJ.....71...64K
        logger.debug("  King model fits")
        for param in ["W_king", "rt_king", "M_king"]:  # /w errorbar
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
                sigma_up=entry["e_" + param],
                sigma_down=entry["e_" + param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))
        for param in ["kinghalf", "kingtrunc", "chi2_king", "chi2red_king"]:
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))
            # TODO: obs = get_or_create()  # something
            # if not created:
            #     self.logger.info("  Found the Observation: {0}".format(obs))
            # else:
            #     self.logger.info("  Created the Observation: {0}".format(obs))

        # Wilson (1975): 1975AJ.....80..175W
        logger.debug("  Wilson model fits")
        for param in ["W_wil", "rt_wil", "M_wil"]:  # /w errorbar
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
                sigma_up=entry["e_" + param],
                sigma_down=entry["e_" + param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))
        for param in ["wilhalf", "wiltrunc", "chi2_wil", "chi2red_wil"]:
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))

        # Limepy: 2015MNRAS.454..576G
        logger.debug("  Limepy model fits")
        for param in [
            "W_lime",
            "g_lime",
            "rt_lime",
            "M_lime",
            "limehalf",
        ]:  # /w errorbar
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
                sigma_up=entry["e_" + param],
                sigma_down=entry["e_" + param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))
        for param in ["chi2_lime", "chi2red_lime"]:
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))

        # SPES: 2017MNRAS.466.3937C; 2019MNRAS.487..147C
        logger.debug("  SPES model fits")
        for param in [
            "W_pe",
            "eta_pe",
            "log1minB_pe",
            "rt_pe",
            "M_pe",
            "pecore",
            "log_fpe",
            "pehalf",
        ]:  # /w errorbar
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
                sigma_up=entry["e_" + param],
                sigma_down=entry["e_" + param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))
        for param in ["chi2_pe", "chi2red_pe"]:
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))

        logger.debug("  Additional de Boer (2019) data")
        for param in ["r_tie", "BGlev", "min_mass", "max_mass"]:
            o = Observation(
                astro_object=gc,
                parameter=Parameter.objects.get(name=parameter_map[param]),
                reference=deBoer19,
                value=entry[param],
            )
            all_observations.append(o)
            logger.debug("    {0}".format(o))

    # Note that we should not have any double Observation instances b/c we
    # nuke all Observations for deBoer19 Reference out of the database first..
    logger.debug(
        "\nInserting {0} objects into SupaHarris database".format(len(all_observations))
    )
    # Because this way we throw a single query at the database (fast), instead
    # of throwing one query per Observation instance (painfully slow)
    Observation.objects.bulk_create(all_observations)
    logger.debug("Done")


def add_deBoer_2019_appendixA(logger):
    deBoer19 = Reference.objects.get(bib_code="2019MNRAS.485.4906D")
    logger.debug("\nInsert de Boer (2019) Appendix A")

    # We first delete all files and Auxiliary instances where Reference is deBoer19
    auxes = Auxiliary.objects.filter(reference=deBoer19)
    [os.remove(f.file.name) for f in auxes if os.path.exists(f.file.name)]
    deleted = auxes.delete()
    if deleted[0] is not 0:
        logger.debug("WARNING: deleted {0} Auxiliary instances".format(deleted))

    files = [f for f in glob.glob(BASEDIR + "profile_fits/*.pdf")]
    gc_names = [
        fix_gc_names(f.split("/")[-1].split("_numdens")[0]).replace("_", "")
        for f in files
    ]
    Nfiles = len(files)
    for i, (gc_name, fname) in enumerate(zip(gc_names, files)):
        gc = AstroObject.objects.get(name=gc_name)
        logger.debug("\n{0}/{1}: {2}".format(i + 1, Nfiles, gc))
        logger.debug("  file: {0}".format(fname))

        # Because the file needs to be open on save() call, right?
        with open(fname, "rb") as f:
            aux = Auxiliary(
                reference=deBoer19,
                astro_object=gc,
                description="de Boer (2019) star cluster fit",
                file=File(f),
                url=None,
            )
            aux.save()
            rename = aux.file.name.replace("aux/", "aux/deBoer2019_")
            os.rename(aux.file.name, rename)
            aux.file.name = rename
            aux.save()
            logger.debug("  goto: {0}".format(aux.file.name))
            logger.debug("  {0}".format(aux))


def add_deBoer_2019_stitched_profiles(logger):
    deBoer19 = Reference.objects.get(bib_code="2019MNRAS.485.4906D")
    logger.debug("\nInsert de Boer (2019) stitched profiles")

    # We first delete all Profile instances that match deBoer19 Reference
    deleted = Profile.objects.filter(reference=deBoer19).delete()
    if deleted[0] is not 0:
        logger.debug("WARNING: deleted {0} Profile instances".format(deleted))

    deBoer_stitched_profiles = parse_deBoer_2019_stitched_profiles(logger)
    Nprofiles = len(deBoer_stitched_profiles)
    for i, (gc_name, profile) in enumerate(deBoer_stitched_profiles.items()):
        gc = AstroObject.objects.get(name=gc_name)
        logger.debug("\n{0}/{1}: {2}".format(i + 1, Nprofiles, gc))
        sh_prof = Profile(
            reference=deBoer19,
            astro_object=gc,
            x=list(profile["rad"]),
            y=list(profile["density"]),
            y_sigma_up=list(profile["density_err"]),
            y_sigma_down=list(profile["density_err"]),
            x_description="R [arcmin]",
            y_description="nGaia [1/arcmin**2]",
        )
        sh_prof.save()


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add de Boer+ (2019) data to the database"

    def handle(self, *args, **options):
        super().handle(
            print_info=True, *args, **options
        )  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        self.logger.info("\n\nRunning the management command '{0}'\n".format(cmd))

        # Add the ADS url (in this particular format). When the Reference
        # instance is saved it will automatically retrieve all relevent info!
        ads_url = "https://ui.adsabs.harvard.edu/abs/2019MNRAS.485.4906D"
        reference, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            self.logger.info("Found the Reference: {0}\n".format(reference))
        else:
            self.logger.info("Created the Reference: {0}\n".format(reference))

        add_deBoer_2019_tableB1(self.logger)
        add_deBoer_2019_appendixA(self.logger)
        add_deBoer_2019_stitched_profiles(self.logger)
