#-*- coding: utf-8 -*-
import os
import sys
import numpy
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models import (
    Auxiliary,
    Reference,
    Parameter,
    Observation,
    AstroObject,
    AstroObjectClassification,
)
from catalogue.utils import map_names_to_ids
from catalogue.utils import PrepareSupaHarrisDatabaseMixin
from data.parse_hilker_2019 import (
    parse_hilker_2019_orbits,
    parse_hilker_2019_combined,
    parse_hilker_2019_radial_velocities,
    parse_baumgardt_2019_mnras_482_5138_table1,
    parse_baumgardt_2019_mnras_482_5138_table4,
    parse_individual_rvs_of_stars_in_field_of_clusters,
)


def create_references(logger):
    logger.info("\ncreate_references")

    # Copy-paste from arXiv:1908.02778v1:
    # Baumgardt (2017) first compared a large grid of 900 N-body models to
    # the velocity dispersion and surface brightness profiles of 50 GGCs
    # in order to determine their masses and mass-to-light ratios.
    #
    # Baumgardt 2017, https://arxiv.org/pdf/1609.08794.pdf
    # http://simbad.u-strasbg.fr/simbad/sim-ref?querymethod=bib&simbo=on&submit=submit+bibcode&bibcode=2017MNRAS.464.2174B
    ads_url = "https://ui.adsabs.harvard.edu/abs/2017MNRAS.464.2174B"
    baumgardt2017, created = Reference.objects.get_or_create(ads_url=ads_url)
    if not created:
        logger.info("  Found the Reference: {0}".format(baumgardt2017))
    else:
        logger.info("  Created the Reference: {0}".format(baumgardt2017))

    # Copy-paste from arXiv:1908.02778v1:
    # Additionally, Sollima & Baumgardt (2017) presented the global mass
    # functions of 35 GGCs based on deep HST photometry in combination
    # with multimass dynamical models.
    #
    # Sollima & Baumgardt (2017), https://arxiv.org/pdf/1708.09529.pdf
    ads_url = "https://ui.adsabs.harvard.edu/abs/2017MNRAS.471.3668S"
    sollima_baumgardt_2017, created = Reference.objects.get_or_create(ads_url=ads_url)
    if not created:
        logger.info("  Found the Reference: {0}".format(sollima_baumgardt_2017))
    else:
        logger.info("  Created the Reference: {0}".format(sollima_baumgardt_2017))

    # Copy-paste from arXiv:1908.02778v1:
    # One year later, Baumgardt & Hilker (2018) deter- mined masses, stellar
    # mass functions, and structural parameters of 112 GGCs by fitting a
    # large set of N-body simulations to their velocity dispersion and surface
    # density profiles.
    #
    # Baumgardt & Hilker 2018, https://arxiv.org/pdf/1804.08359.pdf
    ads_url = "https://ui.adsabs.harvard.edu/abs/2018MNRAS.478.1520B"
    Baumgardt_Hilker_2018, created = Reference.objects.get_or_create(ads_url=ads_url)
    if not created:
        logger.info("  Found the Reference: {0}".format(Baumgardt_Hilker_2018))
    else:
        logger.info("  Created the Reference: {0}".format(Baumgardt_Hilker_2018))

    # Copy-paste from arXiv:1908.02778v1:
    # When Gaia DR2 became public, Baumgardt et al. (2019) presented mean
    # proper motions and space velocities of 154 GGCs and the velocity
    # dispersion profiles of 141 globular clusters based on a combination
    # of Gaia DR2 proper motions with ground-based line-of-sight velocities.
    # The combination of these velocity dispersion profiles with new
    # measurements of the internal mass functions allowed to model the internal
    # kinematics of 144 GGCs, more than 90 per cent of the currently known
    # Milky Way globular cluster population
    #
    # Baumgardt, Hilker, Sollima & Bellini 2019, https://arxiv.org/pdf/1811.01507.pdf
    ads_url = "https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B"
    BHSB2019, created = Reference.objects.get_or_create(ads_url=ads_url)
    if not created:
        logger.info("  Found the Reference: {0}".format(BHSB2019))
    else:
        logger.info("  Created the Reference: {0}".format(BHSB2019))
    # J/MNRAS/482/5138/table1
    # J/MNRAS/482/5138/table4

    # Finally, Sollima, Baumgardt & Hilker (2019) analysed the internal
    # kinematics of 62 GGCs, finding significant rotation in 15 of them.
    # https://arxiv.org/pdf/1902.05895.pdf
    ads_url = "https://ui.adsabs.harvard.edu/abs/2019MNRAS.485.1460S"
    SBH2019, created = Reference.objects.get_or_create(ads_url=ads_url)
    if not created:
        logger.info("  Found the Reference: {0}".format(SBH2019))
    else:
        logger.info("  Created the Reference: {0}".format(SBH2019))

    # For the radial dispersion profiles (of radial velocity and proper motion)
    ads_url = "https://ui.adsabs.harvard.edu/abs/2018MNRAS.473.5591K"
    K2018, created = Reference.objects.get_or_create(ads_url=ads_url)
    if not created:
        logger.info("  Found the Reference: {0}".format(K2018))
    else:
        logger.info("  Created the Reference: {0}".format(K2018))

    ads_url = "https://ui.adsabs.harvard.edu/abs/2015ApJ...803...29W"
    W2015, created = Reference.objects.get_or_create(ads_url=ads_url)
    if not created:
        logger.info("  Found the Reference: {0}".format(W2015))
    else:
        logger.info("  Created the Reference: {0}".format(W2015))


def create_new_gcs(logger, GC):
    logger.info("\ncreate_new_gcs")

    # Create GC that has not been encoutered, and get the altname right
    # Laevens+ 2014: https://ui.adsabs.harvard.edu/abs/2014ApJ...786L...3L
    laevens1, created = AstroObject.objects.get_or_create(
        name="Laevens 1",
        altname="Crater",
    )
    laevens1.classifications.add(GC)
    if created:
        logger.info("  Created: {0}".format(laevens1))
    else:
        logger.info("  Found: {0}".format(laevens1))

    # Minniti+ 2017: https://ui.adsabs.harvard.edu/abs/2017ApJ...838L..14M
    fsr1716, created = AstroObject.objects.get_or_create(
        name="FSR 1716",
    )
    fsr1716 .classifications.add(GC)
    if created:
        logger.info("  Created: {0}".format(fsr1716))
    else:
        logger.info("  Found: {0}".format(fsr1716))

    # Mercer+ 2005: https://ui.adsabs.harvard.edu/abs/2005AJ....129..239K
    # Longmore+ 2011: https://ui.adsabs.harvard.edu/abs/2011MNRAS.416..465L
    mercer5, created = AstroObject.objects.get_or_create(
        name="Mercer 5",
    )
    mercer5.classifications.add(GC)
    if created:
        logger.info("  Created: {0}".format(mercer5))
    else:
        logger.info("  Found: {0}".format(mercer5))


    # TODO: update Ko 1, Ko 2 classification (Paust, Wilson & van Belle 2014)
    # --> several Gyr old Open Clusters removed from Sagittarius dwarf galaxy.
    Koposov1 = AstroObject.objects.get(name="Ko 1")
    Koposov2 = AstroObject.objects.get(name="Ko 2")

    # TODO: GLIMPSE01, GLIMPSE02 (Davies+ 2011): 400-800 Gyr --> intermediate
    # age disc cluster.
    GLIMPSE01 = AstroObject.objects.get(name="GLIMPSE01")
    GLIMPSE02 = AstroObject.objects.get(name="GLIMPSE02")

    # TODO: BH 176 --> old, metal-rich open cluster that could belong to the
    # galactic thick disc (Davoust, Sharina & Donzelli 2011; Sharina+ 2014)
    BH176 = AstroObject.objects.get(name="BH 176")


def add_orbits(logger, name_id_map):
    # The relevant reference for the sky coordinates, distance from the Sun,
    # radial velocity, and proper motions in RA/Dec seems to be Baumgardt+ (2019)
    #     https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B.

    # These measured quantities are then used to do the orbital integrations
    # (for a given Milky Way mass model / analytical potential), giving derived
    # quantities X/Y/Z/U/V/W, R_Peri, R_Apo /w propagated uncertainties.
    # TODO: we may have to convert the heliocentric coordinates to ensure the
    # Baumgardt values are consistent with those quoted by Harris (1996). The
    # exact definition of the coordinate system may differ.

    # The data are available at the website of Holger Baumgardt
    #     https://people.smp.uq.edu.au/HolgerBaumgardt/globular/orbits_table.txt
    # as well as through Vizier
    #     Vizier.get_catalogs("J/MNRAS/482/5138/table1")[0]

    logger.info("\nAdd orbits_table.txt")

    # Relevant Parameter instances
    RA = Parameter.objects.get(name="RA")
    Dec = Parameter.objects.get(name="Dec")
    L = Parameter.objects.get(name="L")
    B = Parameter.objects.get(name="B")
    R_Sun = Parameter.objects.get(name="R_Sun")
    R_Gal = Parameter.objects.get(name="R_Gal")
    X = Parameter.objects.get(name="X")
    Y = Parameter.objects.get(name="Y")
    Z = Parameter.objects.get(name="Z")
    # Heliocentric radial velocity
    v_r = Parameter.objects.get(name="v_r")
    # Radial velocity relative to solar neighbourhood
    # c_LSR = Parameter.objects.get(name="c_LSR")
    R_peri = Parameter.objects.get(name="R_peri")
    R_apo = Parameter.objects.get(name="R_apo")
    pmRA = Parameter.objects.get(name="pmRA")
    pmDec = Parameter.objects.get(name="pmDec")

    # Create new Parameter instances
    U, created = Parameter.objects.get_or_create(name="U",
        defaults={"scale": 1, "unit": "km/s"})
    U.description = "Heliocentric velocity component U"
    U.save()
    if created:
        logger.info("  Created: {0}".format(U))
    else:
        logger.info("  Found: {0}".format(U))
    V, created = Parameter.objects.get_or_create(name="V",
        defaults={"scale": 1, "unit": "km/s"})
    V.description = "Heliocentric velocity component V"
    V.save()
    if created:
        logger.info("  Created: {0}".format(V))
    else:
        logger.info("  Found: {0}".format(V))
    W, created = Parameter.objects.get_or_create(name="W",
        defaults={"scale": 1, "unit": "km/s"})
    W.description = "Heliocentric velocity component W"
    W.save()
    if created:
        logger.info("  Created: {0}".format(W))
    else:
        logger.info("  Found: {0}".format(W))

    rhopmrade, created = Parameter.objects.get_or_create(name="rhopmrade",
        defaults={"scale": 1, "unit": ""})
    rhopmrade.description = "Correlation between proper motion in RA and Dec"
    rhopmrade.save()
    if created:
        logger.info("  Created: {0}".format(rhopmrade))
    else:
        logger.info("  Found: {0}".format(rhopmrade))

    # Relevant Reference
    ref = Reference.objects.get(
        ads_url="https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B")
    logger.info("\n  Using the Reference: {0}".format(ref))

    # Get the data
    data = parse_hilker_2019_orbits(logger)

    nrows = len(data)
    logger.info("\n  Found {0} rows".format(nrows))
    for i, row in enumerate(data):
        if i > 5: break
        logger.info("\n  {0} / {1}".format(i+1, nrows))

        gc_name = row["Cluster"]
        if gc_name in name_id_map:
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            logger.info("    Found GC: {0}{1} for '{2}'".format(gc.name,
                " ({0})".format(gc.altname) if gc.altname else "", gc_name))
        else:
            logger.info("    ERROR: did not find {0}".format(gc_name))
            sys.exit(1)

        # `For IC 1257 and Ter 10 we found that the cluster centres given
        # in Harris (1996) were incorrect.' - Baumgardt+ (2019MNRAS.482.5138B) Section 2.1
        # RA and DEC either come from Harris 1996, or from Goldsbury, Heyl & Richer (2013),
        # except for IC 1257 and Ter 10 (which have been calculated by B19)
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=RA, value=row["RA"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=Dec, value=row["DEC"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=L, value=row["l"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=B, value=row["b"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=R_Sun, value=row["Rsun"], sigma_up=row["ERsun"], sigma_down=row["ERsun"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=R_Gal, value=row["R_GC"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        # TODO: check that this is indeed v_r (Heliocentric radial velocity)
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=v_r, value=row["RV"], sigma_up=row["ERV"], sigma_down=row["ERV"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=pmRA, value=row["mualpha"],
            sigma_up=row["mualpha_err"], sigma_down=row["mualpha_err"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=pmDec, value=row["mu_delta"],
            sigma_up=row["mu_delta_err"], sigma_down=row["mu_delta_err"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        # Correlation between proper motion in RA and DEC
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=rhopmrade, value=row["rhopmrade"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=X, value=row["X"], sigma_up=row["DX"], sigma_down=row["DX"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=Y, value=row["Y"], sigma_up=row["DY"], sigma_down=row["DY"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=Z, value=row["Z"], sigma_up=row["DZ"], sigma_down=row["DZ"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=U, value=row["U"], sigma_up=row["DU"], sigma_down=row["DU"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=V, value=row["V"], sigma_up=row["DV"], sigma_down=row["DV"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=W, value=row["W"], sigma_up=row["DW"], sigma_down=row["DW"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=R_peri, value=row["RPERI"],
            sigma_up=row["RPERI_err"], sigma_down=row["RPERI_err"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=R_apo, value=row["RAP"],
            sigma_up=row["RAP_err"], sigma_down=row["RAP_err"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))


def add_combined(logger, name_id_map):
    logger.info("\n  Add combined_table.txt")
    data = parse_hilker_2019_combined(logger)

    nrows = len(data)
    logger.info("    Found {0} rows".format(nrows))
    for i, row in enumerate(data):
        logger.debug("    {0} / {1}".format(i+1, nrows))

        gc_name = row["Cluster"]
        if gc_name in name_id_map:
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            logger.info("      Found: {0}{1} for '{2}'".format(gc.name,
                " ({0})".format(gc.altname) if gc.altname else "", gc_name))
        else:
            logger.info("      Created: {0}".format(gc_name))


def add_rv(logger, name_id_map):
    logger.info("\n  Add rv.dat")

    ads_url = "https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B"
    BHSB2019 = Reference.objects.get(ads_url=ads_url)
    logger.info("    Using the Reference: {0}".format(BHSB2019))

    ads_url = "https://ui.adsabs.harvard.edu/abs/2018MNRAS.473.5591K"
    K2018 = Reference.objects.get(ads_url=ads_url)
    logger.info("    Using the Reference: {0}".format(K2018))

    ads_url = "https://ui.adsabs.harvard.edu/abs/2015ApJ...803...29W"
    W2015 = Reference.objects.get(ads_url=ads_url)
    logger.info("    Using the Reference: {0}".format(W2015))

    # Parse and iterate through the data
    data = parse_hilker_2019_radial_velocities(logger)
    gc_names = numpy.unique(data["Cluster"])
    ngcs = len(gc_names)
    logger.info("\n    Found {0} GCs /w {1} data points".format(ngcs, len(data)))

    w = " "*8
    for i, gc_name in enumerate(gc_names):
        logger.debug("    {0} / {1}".format(i+1, ngcs))
        if gc_name in name_id_map:
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            logger.info("      Found: {0}{1} for '{2}'".format(gc.name,
                " ({0})".format(gc.altname) if gc.altname else "", gc_name))
        else:
            logger.info("      Created: {0}".format(gc_name))

        igc, = numpy.where(data["Cluster"] == gc_name)
        logger.info("      this GC has {0} data points".format(len(igc)))

        radii = data["radius"][igc]
        velocity_dispersion = data["velocity_dispersion"][igc]
        velocity_dispersion_err_up = data["velocity_dispersion_err_up"][igc]
        velocity_dispersion_err_down = data["velocity_dispersion_err_down"][igc]

        data_type = data["type"][igc]
        # Baumgardt, Hilker, Sollima & Bellini (2019), MNRAS 482, 5138
        rv_from_h19, = numpy.where(data_type == "RV")
        if len(rv_from_h19) > 0:
            logger.debug("{0}RV from H19 --> Reference {1}".format(w, BHSB2019))
            logger.debug("{0}{1}".format(w, radii[rv_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion[rv_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_up[rv_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_down[rv_from_h19]))

        # Kamann et al. (2018), MNRAS, 473, 5591
        rv_from_k18, = numpy.where(data_type == "K18")
        if len (rv_from_k18) > 0:
            logger.debug("{0}RV from K18 --> Reference {1}".format(w, K2018))
            logger.debug("{0}{1}".format(w, radii[rv_from_k18]))
            logger.debug("{0}{1}".format(w, velocity_dispersion[rv_from_k18]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_up[rv_from_k18]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_down[rv_from_k18]))

        # Baumgardt, Hilker, Sollima & Bellini (2019), MNRAS 482, 5138
        pm_from_h19, = numpy.where(data_type == "GDR2")
        if len(pm_from_h19) > 0:
            logger.debug("{0}PM from H19 --> Reference {1}".format(w, BHSB2019))
            logger.debug("{0}{1}".format(w, radii[pm_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion[pm_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_up[pm_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_down[pm_from_h19]))

        # Watkins et al. (2015), ApJ 803, 29
        pm_from_w15, = numpy.where(data_type == "W15")
        if len(pm_from_w15) > 0:
            logger.debug("{0}PM from W15 --> Reference {1}".format(w, W2015))
            logger.debug("{0}{1}".format(w, radii[pm_from_w15]))
            logger.debug("{0}{1}".format(w, velocity_dispersion[pm_from_w15]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_up[pm_from_w15]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_down[pm_from_w15]))

        if i>2: break


def add_baumgardt_2019_mnras_482_5138(logger, name_id_map):
    logger.info("\n  Add Baumgardt (2019) MNRAS 482, 5138")
    table1 = parse_baumgardt_2019_mnras_482_5138_table1()
    table4 = parse_baumgardt_2019_mnras_482_5138_table4()

    nrows = len(table1)
    logger.info("    Found {0} rows in table1".format(nrows))
    # for i, row in enumerate(table1):
    #     logger.debug("    {0} / {1}".format(i+1, nrows))

    nrows = len(table4)
    logger.info("    Found {0} rows in table4".format(nrows))
    return
    for i, row in enumerate(table4):
        logger.debug("    {0} / {1}".format(i+1, nrows))


def add_fits(logger, name_id_map):
    logger.info("\n  Add individual GC fits scraped from Baumgardt website")
    return

    fits = scrape_individual_fits_from_baumgardt_website(logger)
    for gc_name in fits:
        logger.info("    GC name: {0}".format(gc_name))

    return

    for bla in bla:
        aux = Auxiliary(
            reference=bla,
            astro_object=bla,
            path=FilePathField,
            url=URLField
        )


def add_rv_profiles(logger, name_id_map):
    logger.info("\n  Add radial velocity profiles (appendix)")
    data = parse_individual_rvs_of_stars_in_field_of_clusters(logger, debug=False)

    gc_names = numpy.unique(data["Cluster"])
    ngcs = len(gc_names)
    logger.info("    Found {0} GCs /w {1} data points".format(ngcs, len(data)))

    for i, gc_name in enumerate(gc_names):
        logger.debug("    {0} / {1}".format(i+1, ngcs))
        if gc_name in name_id_map:
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            logger.info("      Found: {0}{1} for '{2}'".format(gc.name,
                " ({0})".format(gc.altname) if gc.altname else "", gc_name))
        else:
            logger.info("      Created: {0}".format(gc_name))

        igc, = numpy.where(data["Cluster"] == gc_name)
        logger.info("      this GC has {0} data points".format(len(igc)))


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Hilker+ 2019 data to the SupaHarris database"

    def handle(self, *args, **options):
        super().handle(*args, **options)  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        self.logger.info("\n\nRunning the management command '{0}'".format(cmd))

        # Make sure the required references are available
        create_references(self.logger)

        # Baumgardt+ 2019 (2019MNRAS.482.5138B) Section 2.1
        create_new_gcs(self.logger, self.GC)

        # Get dict that maps (alt)name variations to the id of a GC in SupaHarris
        name_id_map = map_names_to_ids()

        # Add the 6D phase space information plus the Orbit integrations
        add_orbits(self.logger, name_id_map)

        # add_combined(self.logger, name_id_map)
        # add_rv(self.logger, name_id_map)
        # add_baumgardt_2019_mnras_482_5138(self.logger, name_id_map)
        # add_fits(self.logger, name_id_map)
        # add_rv_profiles(self.logger, name_id_map)
