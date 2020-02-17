#-*- coding: utf-8 -*-
import os
import sys
import numpy
import logging
import astropy.units as u

from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models import (
    Auxiliary,
    Reference,
    Parameter,
    Observation,
    AstroObject,
    AstroObjectClassification,
    Profile,
)
from catalogue.utils import map_names_to_ids
from catalogue.utils import PrepareSupaHarrisDatabaseMixin
from data.parse_hilker_2019 import (
    parse_hilker_2019_orbits,
    parse_hilker_2019_combined,
    parse_hilker_2019_radial_velocities,
    parse_baumgardt_2019_mnras_482_5138_table1,
    parse_baumgardt_2019_mnras_482_5138_table4,
    scrape_individual_fits_from_baumgardt_website,
    parse_individual_rvs_of_stars_in_field_of_clusters,
)


def create_references(logger):
    logger.info("\ncreate_references")

    ads_url = "https://ui.adsabs.harvard.edu/abs/2019arXiv190802778H"
    HBSB2019, created = Reference.objects.get_or_create(ads_url=ads_url)
    if not created:
        logger.info("  Found the Reference: {0}".format(HBSB2019))
    else:
        logger.info("  Created the Reference: {0}".format(HBSB2019))

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

    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/fits/clusterlist.html
    # has previously unmentioned GCs, so we create AstroObject instances for those.
    for gc_name in ["BH 140", "ESO 280", "ESO 452", "FSR 1758"]:
        gc, created = AstroObject.objects.get_or_create(
            name=gc_name
        )
        gc.classifications.add(GC)
        if created:
            logger.info("  Created: {0}".format(gc))
        else:
            logger.info("  Found: {0}".format(gc))


def add_orbits(logger, name_id_map):
    # The relevant reference for the sky coordinates, distance from the Sun,
    # radial velocity, and proper motions in RA/Dec seems to be Baumgardt+ (2019)
    #     https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B.

    # These measured quantities are then used to do the orbital integrations
    # (for a given Milky Way mass model / analytical potential), giving derived
    # quantities X/Y/Z/U/V/W, R_Peri, R_Apo /w propagated uncertainties.
    # In particular, the authors use the Irrgang et al. (2013) galactic model.
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
    U.description = "Heliocentric velocity component U [in X direction]"
    U.save()
    if created:
        logger.info("  Created: {0}".format(U))
    else:
        logger.info("  Found: {0}".format(U))
    V, created = Parameter.objects.get_or_create(name="V",
        defaults={"scale": 1, "unit": "km/s"})
    V.description = "Heliocentric velocity component V [in Y direction]"
    V.save()
    if created:
        logger.info("  Created: {0}".format(V))
    else:
        logger.info("  Found: {0}".format(V))
    W, created = Parameter.objects.get_or_create(name="W",
        defaults={"scale": 1, "unit": "km/s"})
    W.description = "Heliocentric velocity component W [in Z direction]"
    W.save()
    if created:
        logger.info("  Created: {0}".format(W))
    else:
        logger.info("  Found: {0}".format(W))

    X_alt, created = Parameter.objects.get_or_create(name="X_alt",
        defaults={"scale": 1, "unit": "kpc"})
    X_alt.description = "Galactic distance component X [from Gal. centre in direction of Sun]"
    X_alt.save()
    if created:
        logger.info("  Created: {0}".format(X_alt))
    else:
        logger.info("  Found: {0}".format(X_alt))
    U_alt, created = Parameter.objects.get_or_create(name="U_alt",
        defaults={"scale": 1, "unit": "km/s"})
    U_alt.description = "Heliocentric velocity component U [in X_alt direction]"
    U_alt.save()
    if created:
        logger.info("  Created: {0}".format(U_alt))
    else:
        logger.info("  Found: {0}".format(U_alt))

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
        ads_url="https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B"
    )
    logger.info("\n  Using the Reference: {0}".format(ref))

    # Get the data
    data = parse_hilker_2019_orbits(logger)

    nrows = len(data)
    logger.info("\n  Found {0} rows".format(nrows))
    for i, row in enumerate(data):
        # if i > 5: break
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

        # Distance from the Gal. centre in direction of Sun (note that the
        # definition is opposite to the more common definition of X from Sun to GC)
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=X_alt, value=row["X"], sigma_up=row["DX"], sigma_down=row["DX"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=Y, value=row["Y"], sigma_up=row["DY"], sigma_down=row["DY"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=Z, value=row["Z"], sigma_up=row["DZ"], sigma_down=row["DZ"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=U_alt, value=row["U"], sigma_up=row["DU"], sigma_down=row["DU"])
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


def arcmin2parsec(arcmin, distance_kpc):
    radian = (arcmin.value*u.arcmin).to(u.rad)
    parsec = numpy.tan(radian) * distance_kpc*1000
    return parsec


def parsec2arcmin(parsec, distance_kpc):
    radian = numpy.arctan2(parsec, distance_kpc*1000)
    arcmin = (radian*u.rad).to(u.arcmin).value
    return arcmin


def add_combined(logger, name_id_map):
    # The relevant reference for the masses, structural parameters, and velocity
    # dispersion profiles seems to be Baumgardt & Hilker (2018)
    #     https://ui.adsabs.harvard.edu/abs/2018MNRAS.478.1520B

    # The authors fit a suite of Nbody models to the observed surface density
    # and dispersion profiles to infer the mass, mass-to-light, core radius,
    # half-mass radius, half-light radius, central density, density inside the
    # half-mass radius, the half-mass relaxation time, the global mass function
    # slope, the mass-weighted (1D) velocity dispersion, and the central escape
    # velocity. The paper does this for 112 GCs, but the data set seems to be
    # updated as it contains 154 entries.

    # The data are available at the website of Holger Baumgardt
    #   https://people.smp.uq.edu.au/HolgerBaumgardt/globular/combined_table.txt

    logger.info("\n  Add combined_table.txt")

    # Relevant Parameter instances
    # RA = Parameter.objects.get(name="RA")
    # Dec = Parameter.objects.get(name="Dec")
    R_Sun = Parameter.objects.get(name="R_Sun")  # to convert radii in pc to '' (or arcmin)
    # R_Gal = Parameter.objects.get(name="R_Gal")
    Mass = Parameter.objects.get(name="Mass")
    V_t = Parameter.objects.get(name="V_t")

    MLv, created = Parameter.objects.get_or_create(name="M/Lv",
        defaults={"scale": 1, "unit": ""})
    MLv.description = "V-band M/L ratio"
    MLv.save()
    if created:
        logger.info("  Created: {0}".format(MLv))
    else:
        logger.info("  Found: {0}".format(MLv))

    sp_r_c = Parameter.objects.get(name="sp_r_c")  # unit: arcmin
    sp_r_h = Parameter.objects.get(name="sp_r_h")  # unit: arcmin

    sp_r_hm, created = Parameter.objects.get_or_create(name="sp_r_hm",
        defaults={"scale": 1, "unit": "arcmin"})  # arcmin for consistency /w sp_r_c and sp_r_h
    sp_r_hm.description = "Half-mass radius (3D)"
    sp_r_hm.save()
    if created:
        logger.info("  Created: {0}".format(sp_r_hm))
    else:
        logger.info("  Found: {0}".format(sp_r_hm))

    sp_r_t, created = Parameter.objects.get_or_create(name="sp_r_t",
        defaults={"scale": 1, "unit": "arcmin"})
    sp_r_t.description = "Tidal radius according to eq. 8 of Webb et al. (2013), ApJ 764, 124"
    sp_r_t.save()
    if created:
        logger.info("  Created: {0}".format(sp_r_t))
    else:
        logger.info("  Found: {0}".format(sp_r_t))

    sp_lg_rho_c, created = Parameter.objects.get_or_create(name="sp_lg_rho_c",
        defaults={"scale": 1, "unit": "log10(MSun/pc^3)"})
    sp_lg_rho_c.description = "Core density"
    sp_lg_rho_c.save()
    if created:
        logger.info("  Created: {0}".format(sp_lg_rho_c))
    else:
        logger.info("  Found: {0}".format(sp_lg_rho_c))

    sp_lg_rho_hm, created = Parameter.objects.get_or_create(name="sp_lg_rho_hm",
        defaults={"scale": 1, "unit": "log10(MSun/pc^3)"})
    sp_lg_rho_hm.description = "Density inside the half-mass radius"
    sp_lg_rho_hm.save()
    if created:
        logger.info("  Created: {0}".format(sp_lg_rho_hm))
    else:
        logger.info("  Found: {0}".format(sp_lg_rho_hm))

    sigma_0 = Parameter.objects.get(name="sigma_0")

    sigma_hm, created = Parameter.objects.get_or_create(name="sigma_hm",
        defaults={"scale": 1, "unit": "MSun/pc^2"})
    sigma_hm.description = "Surface density of stars inside the half-mass radius"
    sigma_hm.save()
    if created:
        logger.info("  Created: {0}".format(sigma_hm))
    else:
        logger.info("  Found: {0}".format(sigma_hm))

    sp_lg_thm, created = Parameter.objects.get_or_create(name="sp_lg_thm",
        defaults={"scale": 1, "unit": "log10(yr)"})
    sp_lg_thm.description = "Half-mass relaxation time"
    sp_lg_thm.save()
    if created:
        logger.info("  Created: {0}".format(sp_lg_thm))
    else:
        logger.info("  Found: {0}".format(sp_lg_thm))

    sp_mf_slope, created = Parameter.objects.get_or_create(name="sp_mf_slope",
        defaults={"scale": 1, "unit": "log10(yr)"})
    sp_mf_slope.description = "Global mass function slope of 0.2 to 0.8 MSun" + \
        " main-sequence stars, alpha_Kroupa = -1.50 over this range."
    sp_mf_slope.save()
    if created:
        logger.info("  Created: {0}".format(sp_mf_slope))
    else:
        logger.info("  Found: {0}".format(sp_mf_slope))

    sp_frac_rem, created = Parameter.objects.get_or_create(name="sp_frac_rem",
        defaults={"scale": 1, "unit": ""})
    sp_frac_rem.description = "Mass fraction of remnants"
    sp_frac_rem.save()
    if created:
        logger.info("  Created: {0}".format(sp_frac_rem))
    else:
        logger.info("  Found: {0}".format(sp_frac_rem))

    sig_v_r = Parameter.objects.get(name="sig_v_r")  # km/s
    v_e_0 = Parameter.objects.get(name="v_e_0")  # km/s

    sp_eta_c, created = Parameter.objects.get_or_create(name="sp_eta_c",
        defaults={"scale": 1, "unit": ""})
    sp_eta_c.description = "Mass segregation parameter from Trenti & van der " + \
        "Marel (2013) for stars in the core and in the mass range 0.5 to 0.8 MSun"
    sp_eta_c.save()
    if created:
        logger.info("  Created: {0}".format(sp_eta_c))
    else:
        logger.info("  Found: {0}".format(sp_eta_c))

    sp_eta_hm, created = Parameter.objects.get_or_create(name="sp_eta_hm",
        defaults={"scale": 1, "unit": ""})
    sp_eta_hm.description = "Mass segregation parameter from Trenti & van der " + \
        "Marel (2013) for stars at the half-mass radius and in the mass range " + \
        "0.5 to 0.8 MSun"
    sp_eta_hm.save()
    if created:
        logger.info("  Created: {0}".format(sp_eta_hm))
    else:
        logger.info("  Found: {0}".format(sp_eta_hm))

    # Relevant Reference
    ref = Reference.objects.get(
        ads_url="https://ui.adsabs.harvard.edu/abs/2018MNRAS.478.1520B"
    )
    logger.info("\n  Using the Reference: {0}".format(ref))

    # To retrieve sp_r_c, sp_r_h [in arcmin] from Harris (1996)
    h96e10 = Reference.objects.get(
        ads_url="https://ui.adsabs.harvard.edu/abs/1996AJ....112.1487H"
    )

    # If we want to retrieve Observation for R_Sun created in add_orbits method above
    # B19 = Reference.objects.get(
    #     ads_url="https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B"
    # )

    # Get the data
    data = parse_hilker_2019_combined(logger)

    # TODO: "Clusters where the mass had to be estimated based on the
    # total luminosity are shown in italics."
    mass_from_luminosity = [
        "FSR 1735", "IC 1257", "Ter 2", "Djor 1", "UKS 1", "Ter 9",
        "Ter 10", "2MASS-GC01", "2MASS-GC02", "Ter 12",
    ]

    # TODO: "Distances with error bars are derived by us, the other distances
    # are taken from the literature"
    # The table at https://people.smp.uq.edu.au/HolgerBaumgardt/globular/parameter.html
    # does contain error bars for R_Sun. However, the file `combined_table.txt'
    # does not the contain error bars on distances ...
    # The `orbits_table.txt', on the other hand, provides the distance error `ERsun'

    nrows = len(data)
    logger.info("\n  Found {0} rows".format(nrows))
    for i, row in enumerate(data):
        # if i > 5: break
        logger.debug("\n  {0} / {1}".format(i+1, nrows))

        gc_name = row["Cluster"]
        if gc_name in name_id_map:
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            logger.info("    Found: {0}{1} for '{2}'".format(gc.name,
                " ({0})".format(gc.altname) if gc.altname else "", gc_name))
        else:
            logger.info("    ERROR: did not find {0}".format(gc_name))
            sys.exit(1)

        if gc_name in mass_from_luminosity:
            # TODO: what do we do with this information?
            logger.info("    TODO: Mass taken from luminosity")

        # Added above in add_orbits method.
        # row["RA"]
        # row["DEC"]
        # value=row["R_Sun"]
        # value=row["R_GC"]

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=Mass, value=row["Mass"], sigma_up=row["DM"], sigma_down=row["DM"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        # Baumgardt website: Apparent V-band magnitude and an approximate error
        # SupaHarris: Integrated V magnitude
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=V_t, value=row["V"], sigma_up=row["V_err"], sigma_down=row["V_err"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=MLv, value=row["ML_V"], sigma_up=row["ML_V_err"], sigma_down=row["ML_V_err"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))


        # Baumgardt website: Core radius using Spitzer (1987) definition, value in parsec
        # SupaHarris: King core radius [arcmin].
        # TODO: compare both definitions
        rc_parsec = row["rc"]

        # Compare to Harris (1996) values, converted from arcmin to parsec. Need distance.
        # i) either use distance from Harris (1996),
        # distance = Observation.objects.filter(reference=h96e10, astro_object=gc,
        #     parameter=R_Sun).first()
        # ii) or use distance already loaded into SupaHarris
        # distance = Observation.objects.filter(reference=B19, astro_object=gc,
        #     parameter=R_Sun).first()
        # iii) or use the distance provided in this dataset, i.e. row["R_Sun"]
        # --> we opt for iii.
        distance_kpc = row["R_Sun"]

        # Baumgardt value, converted from parsec to arcmin
        rc_arcmin = parsec2arcmin(rc_parsec, distance_kpc)
        logger.debug("    King Core radius: {0} parsec".format(rc_parsec))
        logger.debug("      --> {0:.2f} arcmin".format(rc_arcmin))

        # Harris (1996) value, converted from arcmin to parsec
        rc_h96 = Observation.objects.filter(astro_object=gc, parameter=sp_r_c,
            reference=h96e10).first()  # arcmin
        if rc_h96:  # checks that the instance exists
            if rc_h96.value:  # checks that the instance has a value not None
                rc_h96_parsec = arcmin2parsec(rc_h96, distance_kpc)
                logger.debug("    Comparison: {0}, value in arcmin".format(rc_h96))
                logger.debug("      --> {0:.2f} parsec".format(rc_h96_parsec))
            else:
                logger.debug("    Comparison: NO VALUE IN Harris (1996)!")
        else:
            logger.debug("    Comparison: NO INSTANCE IN Harris (1996)!")

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_r_c, value=rc_arcmin)
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))


        # Baumgardt website: Projected half-light radius
        # SupaHarris: Half-light radius. TODO: compare to Harris (1996) definition
        rhl_parsec = row["rhl"]

        # Baumgardt value, converted from parsec to arcmin
        rhl_arcmin = parsec2arcmin(rhl_parsec, distance_kpc)
        logger.debug("    Half-light radius: {0} parsec".format(rhl_parsec))
        logger.debug("      --> {0:.2f} arcmin".format(rhl_arcmin))
        rhl_h96 = Observation.objects.filter(astro_object=gc, parameter=sp_r_h,
            reference=h96e10).first()  # arcmin
        if rhl_h96:  # checks that the instance exists
            if rhl_h96.value:  # checks that the instance has a value not None
                rhl_h96_parsec = arcmin2parsec(rhl_h96, distance_kpc)
                logger.debug("    Comparison: {0}, value in arcmin".format(rhl_h96))
                logger.debug("      --> {0:.2f} parsec".format(rhl_h96_parsec))
            else:
                logger.debug("    Comparison: NO VALUE IN Harris (1996)!")
        else:
            logger.debug("    Comparison: NO INSTANCE IN Harris (1996)!")

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_r_h, value=rhl_arcmin)
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))


        rhm_parsec = row["rhm"]
        rhm_arcmin = parsec2arcmin(rhm_parsec, distance_kpc)
        logger.debug("    Half-mass radius: {0} parsec".format(rhm_parsec))
        logger.debug("      --> {0:.2f} arcmin".format(rhm_arcmin))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_r_hm, value=rhm_arcmin)
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))


        rt_parsec = row["rt"]
        rt_arcmin = parsec2arcmin(rt_parsec, distance_kpc)
        logger.debug("    Tidal radius: {0} parsec".format(rt_parsec))
        logger.debug("      --> {0:.2f} arcmin".format(rt_arcmin))
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_r_t, value=rt_arcmin)
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))


        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_lg_rho_c, value=row["rho_c"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_lg_rho_hm, value=row["rho_hm"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        # Baumgardt website: not explicitly mentioned. Just pops up in combined_table.txt
        # SupaHarris: Central surface density of stars at the cluster center in MSun/pc^2
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sigma_0, value=row["sig_c"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        # Baumgardt website: not explicitly mentioned. Just pops up in combined_table.txt
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sigma_hm, value=row["sig_hm"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_lg_thm, value=row["lgTrh"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_mf_slope, value=row["MF"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_frac_rem, value=row["F_REM"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        # Baumgardt website: Central 1D velocity dispersion
        # SupaHarris: Central velocity dispersion
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sig_v_r, value=row["sig0"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        # Baumgardt website: Central escape velocity
        # SupaHarris: Central escape velocity
        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=v_e_0, value=row["vesc"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_eta_c, value=row["etac"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))

        o, created = Observation.objects.get_or_create(reference=ref, astro_object=gc,
            parameter=sp_eta_hm, value=row["etah"])
        logger.debug("    {0}: {1}".format("Created" if created else "Found", o))


def add_rv(logger, name_id_map):
    # Velocity dispersion profiles as function of radius, either for the
    # dispersion in radial velocity, or for the dispersion in proper motion.

    # The data are available at the website of Holger Baumgardt
    #     https://people.smp.uq.edu.au/HolgerBaumgardt/globular/rv.dat
    # TODO: rv.dat does not include Nstar, whereas the DataTable at the website
    # does. However, our Profile model also does not have support for Nstar,
    # but it could be added as a seperate Profile instance /w x=radii, y=Nstar?

    logger.info("\n  Add rv.dat\n")

    # Relevant Reference instances
    ads_url = "https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B"
    BHSB2019 = Reference.objects.get(ads_url=ads_url)
    logger.info("  Using the Reference: {0}".format(BHSB2019))

    ads_url = "https://ui.adsabs.harvard.edu/abs/2018MNRAS.473.5591K"
    K2018 = Reference.objects.get(ads_url=ads_url)
    logger.info("  Using the Reference: {0}".format(K2018))

    ads_url = "https://ui.adsabs.harvard.edu/abs/2015ApJ...803...29W"
    W2015 = Reference.objects.get(ads_url=ads_url)
    logger.info("  Using the Reference: {0}".format(W2015))

    # Parse and iterate through the data
    data = parse_hilker_2019_radial_velocities(logger)
    gc_names = numpy.unique(data["Cluster"])
    ngcs = len(gc_names)
    logger.info("\n  Found {0} GCs /w {1} data points".format(ngcs, len(data)))

    w = " "*6
    for i, gc_name in enumerate(gc_names):
        # if i > 5: break
        logger.debug("\n  {0} / {1}".format(i+1, ngcs))

        if gc_name in name_id_map:
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            logger.info("    Found: {0}{1} for '{2}'".format(gc.name,
                " ({0})".format(gc.altname) if gc.altname else "", gc_name))
        else:
            logger.info("    ERROR: did not find {0}".format(gc_name))
            sys.exit(1)

        igc, = numpy.where(data["Cluster"] == gc_name)
        logger.info("    this GC has {0} data points".format(len(igc)))

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
            p, created = Profile.objects.get_or_create(reference=BHSB2019, astro_object=gc,
                x=list(radii[rv_from_h19]),
                x_description="Radius [arcsec]",
                y=list(velocity_dispersion[rv_from_h19]),
                y_description="Velocity dispersion (radial velocity) [km/s]",
                y_sigma_up=list(velocity_dispersion_err_up[rv_from_h19]),
                y_sigma_down=list(velocity_dispersion_err_down[rv_from_h19])
            )
            logger.debug("    {0}: {1}".format("Created" if created else "Found", p))
        # Kamann evelocity_dispersion_err_down[rv_from_h19]))t al. (2018), MNRAS, 473, 5591
        rv_from_k18, = numpy.where(data_type == "K18")
        if len (rv_from_k18) > 0:
            logger.debug("{0}RV from K18 --> Reference {1}".format(w, K2018))
            logger.debug("{0}{1}".format(w, radii[rv_from_k18]))
            logger.debug("{0}{1}".format(w, velocity_dispersion[rv_from_k18]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_up[rv_from_k18]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_down[rv_from_k18]))
            p, created = Profile.objects.get_or_create(reference=K2018, astro_object=gc,
                x=list(radii[rv_from_k18]),
                x_description="Radius [arcsec]",
                y=list(velocity_dispersion[rv_from_k18]),
                y_description="Velocity dispersion (radial velocity) [km/s]",
                y_sigma_up=list(velocity_dispersion_err_up[rv_from_k18]),
                y_sigma_down=list(velocity_dispersion_err_down[rv_from_k18])
            )
            logger.debug("    {0}: {1}".format("Created" if created else "Found", p))

        # Baumgardt, Hilker, Sollima & Bellini (2019), MNRAS 482, 5138
        pm_from_h19, = numpy.where(data_type == "GDR2")
        if len(pm_from_h19) > 0:
            logger.debug("{0}PM from H19 --> Reference {1}".format(w, BHSB2019))
            logger.debug("{0}{1}".format(w, radii[pm_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion[pm_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_up[pm_from_h19]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_down[pm_from_h19]))
            p, created = Profile.objects.get_or_create(reference=BHSB2019, astro_object=gc,
                x=list(radii[pm_from_h19]),
                x_description="Radius [arcsec]",
                y=list(velocity_dispersion[pm_from_h19]),
                y_description="Velocity dispersion (proper motion) [km/s]",
                y_sigma_up=list(velocity_dispersion_err_up[pm_from_h19]),
                y_sigma_down=list(velocity_dispersion_err_down[pm_from_h19])
            )
            logger.debug("    {0}: {1}".format("Created" if created else "Found", p))

        # Watkins et al. (2015), ApJ 803, 29
        pm_from_w15, = numpy.where(data_type == "W15")
        if len(pm_from_w15) > 0:
            logger.debug("{0}PM from W15 --> Reference {1}".format(w, W2015))
            logger.debug("{0}{1}".format(w, radii[pm_from_w15]))
            logger.debug("{0}{1}".format(w, velocity_dispersion[pm_from_w15]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_up[pm_from_w15]))
            logger.debug("{0}{1}".format(w, velocity_dispersion_err_down[pm_from_w15]))
            p, created = Profile.objects.get_or_create(reference=W2015, astro_object=gc,
                x=list(radii[pm_from_w15]),
                x_description="Radius [arcsec]",
                y=list(velocity_dispersion[pm_from_w15]),
                y_description="Velocity dispersion (proper motion) [km/s]",
                y_sigma_up=list(velocity_dispersion_err_up[pm_from_w15]),
                y_sigma_down=list(velocity_dispersion_err_down[pm_from_w15])
            )
            logger.debug("    {0}: {1}".format("Created" if created else "Found", p))


def add_baumgardt_2019_mnras_482_5138(logger, name_id_map):
    logger.info("\n  Add Baumgardt (2019) MNRAS 482, 5138")

    # Table1 --> should be the same data as added in add_orbits
    table1 = parse_baumgardt_2019_mnras_482_5138_table1()
    # Table4 --> should be the same data as added in add_rv
    table4 = parse_baumgardt_2019_mnras_482_5138_table4()

    nrows = len(table1)
    logger.info("    Found {0} rows in table1".format(nrows))
    # for i, row in enumerate(table1):
    #     logger.debug("    {0} / {1}".format(i+1, nrows))

    nrows = len(table4)
    logger.info("    Found {0} rows in table4".format(nrows))
    # for i, row in enumerate(table4):
    #     logger.debug("    {0} / {1}".format(i+1, nrows))


def add_fits(logger, name_id_map):
    logger.info("\n  Add individual GC fits scraped from Baumgardt website")

    # Relevant Reference
    ref = Reference.objects.get(
        ads_url="https://ui.adsabs.harvard.edu/abs/2019arXiv190802778H")
    logger.info("\n  Using the Reference: {0}".format(ref))

    # Get the data
    fits = scrape_individual_fits_from_baumgardt_website(logger)
    ngcs = len(fits)
    logger.info("\n  Found {0} GCs".format(ngcs))

    for i, gc_name in enumerate(fits.keys()):
        if i > 5: break
        logger.debug("\n  {0} / {1}".format(i+1, ngcs))

        if gc_name in name_id_map:
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            logger.info("  Found: {0}{1} for '{2}'".format(gc.name,
                " ({0})".format(gc.altname) if gc.altname else "", gc_name))
        else:
            logger.info("  ERROR: did not find {0}".format(gc_name))
            sys.exit(1)

        for figure in fits[gc_name]:
            if figure == "url": continue
            fname = fits[gc_name][figure]["fname"]
            img_src = fits[gc_name][figure]["img_src"]
            logger.debug("    fname: {0}".format(fname))
            logger.debug("    img_src: {0}".format(img_src))

            aux, created = Auxiliary.objects.get_or_create(
                reference=ref,
                astro_object=gc,
                path=FilePathField,
                url=img_src
            )
            logger.debug("    {0}: {1}".format("Created" if created else "Found", aux))


def add_rv_profiles(logger, name_id_map):
    # https://people.smp.uq.edu.au/HolgerBaumgardt/globular/appendix/appendix.html

    # Baumgardt & Hilker (2018)
    #     https://ui.adsabs.harvard.edu/abs/2018MNRAS.478.1520B

    logger.info("\n  Add radial velocity profiles (appendix)")

    # Relevant Reference
    ref = Reference.objects.get(
        ads_url="https://ui.adsabs.harvard.edu/abs/2018MNRAS.478.1520B")
    logger.info("\n  Using the Reference: {0}".format(ref))

    # Get the data
    data = parse_individual_rvs_of_stars_in_field_of_clusters(logger, debug=False)

    gc_names = numpy.unique(data["Cluster"])
    ngcs = len(gc_names)
    logger.info("\n  Found {0} GCs /w {1} data points".format(ngcs, len(data)))

    for i, gc_name in enumerate(gc_names):
        logger.debug("\n  {0} / {1}".format(i+1, ngcs))
        if gc_name in name_id_map:
            gc = AstroObject.objects.get(id=name_id_map[gc_name])
            logger.info("    Found: {0}{1} for '{2}'".format(gc.name,
                " ({0})".format(gc.altname) if gc.altname else "", gc_name))
        else:
            logger.info("    ERROR: did not find {0}".format(gc_name))
            sys.exit(1)

        igc, = numpy.where(data["Cluster"] == gc_name)
        logger.info("    this GC has {0} data points".format(len(igc)))

        # TODO: 2MASS ID can be used to create an AstroObject /w AstroObjectClassifaction
        # Star, and with a parent-child relationship of AstroObject w/ self. The
        # parent would be gc. However, not all entries of the individual stars
        # have 2MASS ID, so how would we handle insertion of stars without an ID?

        # Parameters would be RA, DEC, Radial Velocity (/w error), J_mag, and K_mag.
        # Possibly also P_Mem (probability that a star is a cluster member)
        # DCEN is the distance of the star to the cluster center, which can be
        # calculated given RA, Dec, and the centroid of the cluster itself.


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
        # add_orbits(self.logger, name_id_map)

        # Add the structural parameters
        add_combined(self.logger, name_id_map)
        return

        # Add the velocity dispersion profiles
        # add_rv(self.logger, name_id_map)

        # Add the plots that live at the Holger Baumgardt website
        add_fits(self.logger, name_id_map)

        # TODO: add data of individual stars in the GCs
        # add_rv_profiles(self.logger, name_id_map)
