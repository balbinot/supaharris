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


def create_Reference_instances_for_bica_refs(verbose=False):
    references = dict()
    bica_references = parse_bica_2019_refs()
    nrefs = len(bica_references)
    for i, (ref_code, [ref, bib_code, cat]) in enumerate(bica_references.items()):
        if verbose:
            print("Entry {0}/{1}".format(i+1, nrefs))
            print("  ref_code: {0}".format(ref_code))
            print("  ref: {0}".format(ref))
            print("  bib_code: {0}".format(bib_code))
            print("  cat: {0}".format(cat))

        ads_url = "https://ui.adsabs.harvard.edu/abs/{0}".format(bib_code)
        if bib_code == "-------------------":
            reference, created = Reference.objects.get_or_create(
                ads_url="https://example.com/{0}".format(ref_code),
                bib_code=ref_code,
            )
            reference.title = ref; reference.save()
        else:
            reference, created = Reference.objects.get_or_create(ads_url=ads_url)
        setattr(Reference, ref_code, reference)
        references[ref_code] = reference

        if verbose: print("{0} the Reference: {1}\n".format("Created" if created else "Found", ref_code))
    return references


def combine_tables(t2, t3, t4, t5):
    keys = list(set(
        list(t2.keys()) + list(t3.keys()) + list(t4.keys()) + list(t5.keys())
    ))
    print("Total (unique) keys: {0}".format(len(keys)))

    combined = dict()
    for k in keys:
        combined[k] = dict()
        combined[k]["t2"] = t2.get(k, None)
        combined[k]["t3"] = t3.get(k, None)
        combined[k]["t4"] = t4.get(k, None)
        combined[k]["t5"] = t5.get(k, None)

    return combined


def get_astro_object(bica_designations, astro_object_names, astro_object_instances):
    for d in bica_designations:
        if d in astro_object_names:
            # astro_object_names[d] --> pk of the instance
            # astro_object_instances[pk] --> astro_object instance
            astro_object = astro_object_instances[astro_object_names[d]]
            print("  AstroObject found: {0}".format(astro_object))
            break
    else:
        astro_object = None
        print("  AstroObject not found for bica_designations: {0}".format(bica_designations))

    return astro_object


def get_astro_object_classifications(bica_classifications, astro_object_classifications):
    classifications = []
    for d in bica_classifications:
        try:
            classifications.append(astro_object_classifications[d])
        except KeyError as e:
            raise

    return classifications



def build_astro_object_instances_for_t3(t3, references, aos, ao_names, aocs):
    astro_objects = list()

    for i, (ref, data) in enumerate(t3.items()):
        # if i > 10: break
        glon, glat, sky_coord, rah, ram, ras, de_sign, ded, dem, des, \
            sky_coord2, diama, diamb, name, obj_class1, obj_class2, comments \
            = data

        found_ao = False
        try:
            print("{0} --> {1}".format(ref, references[ref]))
        except KeyError:
            print("ERROR: ref {0} is not known in references...".format(ref))
            sjenk = input("Press any key to continue\n")
            continue
        print("  name: {0}".format(name))
        for n in name.split(","):
            print("    n: {0}".format(n))
            if n in ao_names.keys():
                found_ao = True
                ao_id = ao_names[n]
                ao = aos[ao_id]
                print("      Found AstroObject: {0}".format(ao))
                sjenk = input("Press any key to continue")
                break
        else:
            print("  Creating new AstroObject")
            sjenk = input("Press any key to continue")

        print("  obj_class1: {0}".format(obj_class1))
        if obj_class1:
            aoc1 = aocs[obj_class1]
            print("    --> aoc1: {0}".format(aoc1))
        print("  obj_class2: {0}".format(obj_class2))
        if obj_class2:
            aoc2 = aocs[obj_class2]
            print("    --> aoc2: {0}".format(aoc2))
        print("  comments: {0}".format(comments))
        print("")


def build_observation_instances_for_t3(t3, references, ps):
    observations = list()
    (Glon, Glat, RA, Dec, CatItem, Diam_a, Diam_b, U, V, W) = ps

    for i, (ref, data) in enumerate(t3.items()):
        if i > 10: break
        print(ref, data)


    return observations


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Bica+ 2019 data to the database"

    def handle(self, *args, **options):
        super().handle(*args, **options)  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        print("\n\nRunning the management command '{0}'\n".format(cmd))

        # Get or create a Reference instance for the Bica+ 2019 paper itself
        ads_url = "https://ui.adsabs.harvard.edu/abs/2019AJ....157...12B"
        bica2019, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(bica2019))
        else:
            print("Created the Reference: {0}\n".format(bica2019))


        # 1) Parse and get or create Reference instances for refs.dat
        print("Creating Reference instances for refs.dat")
        references = create_Reference_instances_for_bica_refs()
        print("Found {0} references\n".format(len(references)))


        # Create Parameter instances that we have not encountered before
        #
        # Note that CatItem = Parameter.objects.get(name="CatItem") will be
        # used to create an Observation(parameter=CatItem, reference=bica2019,
        # astro_object=ao).
        print("Creating Parameter instances for new Parameters")
        for bica_parameter, bica_description, bica_unit in zip(
                ["CatItem", "Diam_a", "Diam_b", "U", "V", "W"],
                ["Catalogue item: AstroObject is included in a Reference",
                 "Major axis diameter", "Minor axis diameter",
                 "Heliocentric velocity component, positive towards the Galactic anticenter",
                 "Heliocentric velocity component, positive towards direction of Galactic rotation",
                 "Heliocentric velocity component, positive towards the North Galactic Pole"],
                ["", "arcmin", "arcmin", "km/h", "km/h", "km/h"]):
            p, created = Parameter.objects.get_or_create(
                name=bica_parameter,
                # 'defaults' are not used for filtering, but it is used if the instance is created
                defaults={"scale": 1.0}
            )
            if created:
                p.description = bica_description
                p.unit = bica_unit
                p.save()

            # Here we dynamically set a variable using the str bica_parameter,
            # and set it to the given Parameter instance. This means that, for
            # example, the variables U, V, and W will be available and we can
            # use those later on to initialise Observation instances!
            globals()[bica_parameter] = p
            print("  {0} the Parameter: {1}".format("Created" if created else "Found", p))

        # Parse the Bica data
        verbose = True if self.verbosity >= 1 else False
        debug = True if self.verbosity >= 2 else False
        t2 = parse_bica_2019_table2(verbose=verbose)
        t3 = parse_bica_2019_table3(verbose=verbose, debug=debug)
        t4 = parse_bica_2019_table4(verbose=verbose)
        t5 = parse_bica_2019_table5(verbose=verbose)
        # combined = combine_tables(t2, t3, t4, t5)
        # nrefs = len(combined)
        # print("INFO: found {0} references in the combined tables".format(nrefs))
        # unknown_references = [k for k in combined.keys() if k not in references]
        # print("WARNING: found {0} unknown_references".format(len(unknown_references)))

        # 2) Table 2 gives a list of Class, Nobj, Name/Acrynum, REF.
        # These data are not ingested into SupaHarris at this point.

        # 3) Table 3 has 10978 entries of Glon, Glat, RA, Dec,
        # diameter of major and minor axis, Class, Name/Acrynym, and REF code.
        # We create an Observation instance where Name/Acronym is used to retrieve
        # the relevant AstroObject (ao), Class is added as AstroObjectClassification
        # to the ao, and Glon/Glat/RA/Dec/Diam_a/Diam_b is used as Parameter. We
        # use the REF code to retrieve the Reference instance to set to the
        # Observation instance (so not the bica2019 Reference). We did create
        # a new Parameter instance `CatItem` above, which we use to create a new
        # Observation(parameter=CatItem, reference=bica2019, astro_object=ao).

        # 4) Table 4 has 242 entries of U, V, W, Glon, Glat, Diam_a, Diam_b.
        # We create an Observation for AstroObject retrieved using Name, which
        # we give AstroObjectClassification for Class1, Class2, and set Reference
        # using the REF code.

        # Retrieve Parameter instances that are available in Supaharris
        Glon = Parameter.objects.get(name="L")
        Glat = Parameter.objects.get(name="B")
        RA = Parameter.objects.get(name="RA")
        Dec = Parameter.objects.get(name="Dec")
        print("\nWe now have the following relevant Parameter instances:")
        print("  RA: {0}".format(RA))
        print("  Dec: {0}".format(Dec))
        print("  Glon: {0}".format(Glon))
        print("  Glat: {0}".format(Glat))
        # The Parameter instances below are added to the globals() in the block
        # 'Create Parameter instances that we have not encountered before' above
        print("  CatItem: {0}".format(CatItem))
        print("  Diam_a: {0}".format(Diam_a))
        print("  Diam_b: {0}".format(Diam_b))
        print("  U: {0}".format(U))
        print("  V: {0}".format(V))
        print("  W: {0}\n".format(W))
        ps = (Glon, Glat, RA, Dec, CatItem, Diam_a, Diam_b, U, V, W)

        # Here we create a dictionary that maps the names of known AstroObject
        # instances in supaharris to its pk to retrieve them later on
        aos = dict()
        ao_names = dict()
        for ao in AstroObject.objects.iterator():
            if ao.name: ao_names[ao.name] = ao.pk
            if "Pal " in ao.name:
                ao_names[ao.name.replace("Pal ", "Palomar ")] = ao.pk
            if "Palomar " in ao.name:
                ao_names[ao.name.replace("Palomar ", "Pal ")] = ao.pk
            if "Ter " in ao.name:
                ao_names[ao.name.replace("Ter ", "Terzan ")] = ao.pk
            if "Terzan " in ao.name:
                ao_names[ao.name.replace("Terzan ", "Ter ")] = ao.pk
            if ao.altname:
                ao_names[ao.altname] = ao.pk
                if "Pal " in ao.altname:
                    ao_names[ao.altname.replace("Pal ", "Palomar ")] = ao.pk
                if "Palomar " in ao.altname:
                    ao_names[ao.altname.replace("Palomar ", "Pal ")] = ao.pk
                if "Ter " in ao.altname:
                    ao_names[ao.altname.replace("Ter ", "Terzan ")] = ao.pk
                if "Terzan " in ao.altname:
                    ao_names[ao.altname.replace("Terzan ", "Ter ")] = ao.pk
            aos[ao.pk] = ao

        # Create a dictionary that maps the AstroObjectClassification abbreviations
        # to the instance. This way we query the database only once, not once for
        # each entry in Bica+ 2019
        aocs = dict()
        for aoc in AstroObjectClassification.objects.iterator():
            if aoc.abbreviation:
                aocs[aoc.abbreviation] = aoc

        # We want to create Observation instances, but if we do so using get_or_create
        # we query our database once for every instance in the Bica table. The database
        # kinda does not like this, so we save Observation instances to a list. This way
        # we can pack the database communication in a bulk query, see the Django docs
        # for details: https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
        astro_objects_t3 = build_astro_object_instances_for_t3(t3, references, aos, ao_names, aocs)
        # AstroObject.objects.bulk_create(astro_objects_t3)
        observations_t3 = build_observation_instances_for_t3(t3, references, ps, aos, ao_names, aocs)
        # Observation.objects.bulk_create(observations_t3)
