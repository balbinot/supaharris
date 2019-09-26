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


class Command(PrepareSupaHarrisDatabaseMixin, BaseCommand):
    help = "Add Bica+ 2019 data to the database"

    def handle(self, *args, **options):
        super().handle(print_info=True, *args, **options)  # to run our Mixin modifications

        cmd = __file__.split("/")[-1].replace(".py", "")
        print("\n\nRunning the management command '{0}'\n".format(cmd))

        # Get or create a Reference instance for the Bica+ 2019 paper itself
        ads_url = "https://ui.adsabs.harvard.edu/abs/2019AJ....157...12B"
        bica2019, created = Reference.objects.get_or_create(ads_url=ads_url)
        if not created:
            print("Found the Reference: {0}\n".format(bica2019))
        else:
            print("Created the Reference: {0}\n".format(bica2019))

        # Parse the Bica data
        t2 = parse_bica_2019_table2(verbose=verbose)
        t3 = parse_bica_2019_table3(verbose=verbose, debug=debug)
        t4 = parse_bica_2019_table4(verbose=verbose)
        t5 = parse_bica_2019_table5(verbose=verbose)

        # Parse and get or create Reference instances for refs.dat
        references = create_Reference_instances_for_bica_refs()
        print("INFO: found {0} references".format(len(references)))
        combined = combine_tables(t2, t3, t4, t5)
        nrefs = len(combined)
        print("INFO: found {0} references in the combined tables".format(nrefs))
        unknown_references = [k for k in combined.keys() if k not in references]
        print("WARNING: found {0} unknown_references".format(len(unknown_references)))

        # Create Parameter instances that we have not encountered before
        for bica_parameter, bica_description, bica_unit in zip(
                ["CatItem", "Diam_a", "Diam_b", "U", "V", "W"],
                ["Catalogue item: AstroObject is included in a Reference"
                 "Major axis diameter", "Minor axis diameter",
                 "Heliocentric velocity component, positive towards the Galactic anticenter",
                 "Heliocentric velocity component, positive towards direction of Galactic rotation",
                 "Heliocentric velocity component, positive towards the North Galactic Pole"],
                ["arcmin", "arcmin", "km/h", "km/h", "km/h"]):
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
            print("{0} the Parameter: {1}".format("Created" if created else "Found", p))

        # Retrieve Parameter instances that are available in Supaharris
        RA = Parameter.objects.get(name="RA")
        Dec = Parameter.objects.get(name="Dec")
        Glon = Parameter.objects.get(name="L")
        Glat = Parameter.objects.get(name="B")
        print("\nRelevant Parameter instances:")
        print("  RA: {0}".format(RA))
        print("  Dec: {0}".format(Dec))
        print("  Glon: {0}".format(Glon))
        print("  Glat: {0}".format(Glat))
        print("  Diam_a: {0}".format(Diam_a))
        print("  Diam_b: {0}".format(Diam_b))
        print("  U: {0}".format(U))
        print("  V: {0}".format(V))
        print("  W: {0}\n".format(W))

        # We want to create Observation instances, but if we do so using get_or_create
        # we query our database once for every instance in the Bica table. The database
        # kinda does not like this, so we save Observation instances to a list. This way
        # we can pack the database communication in a bulk query, see the Django docs
        # for details: https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
        observations = list()

        # Here we create a dictionary that maps the names of known AstroObject
        # instances in supaharris to its pk to retrieve them later on
        astro_object_names = dict()
        astro_object_instances = dict()
        for o in AstroObject.objects.iterator():
            astro_object_names[o.name] = o.pk
            astro_object_names[o.altname] = o.pk
            astro_object_instances[o.pk] = o

        # Create a dictionary that maps the AstroObjectClassification abbreviations
        # to the instance. This way we query the database only once, not once for
        # each entry in Bica+ 2019
        astro_object_classifications = dict()
        for c in AstroObjectClassification.objects.iterator():
            if c.abbreviation:
                astro_object_classifications[c.abbreviation] = c

        verbose = True
        debug = True
        for i, ref_code in enumerate(combined.keys()):
            if debug and i > 9: break
            ref = references[ref_code]
            print("\nReference {0}/{1}: {2} --> {3}".format(i+1, nrefs, ref_code, ref))
            if debug:
                print("  {0}".format(combined[ref_code]))

            # TODO: we do not have support for multiple references for an Observation.
            # In this case we should add bica2019 as well as references[ref_code]?
            # obs = Observation(parameter=CatItem, reference=bica2019, astro_object=?, value=True)
            # print(obs)

            # The point of Table4 seems to present measurements kinematics
            if combined[ref_code]["t4"]:
                if verbose: print("\n  Found an entry in Table4")
                if debug: print("    {0}".format(combined[ref_code]["t4"]))

                bica_designations = combined[ref_code]["t4"][7].split(",")
                astro_object = get_astro_object(bica_designations,
                    astro_object_names, astro_object_instances)

                bica_classifications = combined[ref_code]["t4"][8].split(",")
                classifications = get_astro_object_classifications(
                    bica_classifications, astro_object_classifications)
                if verbose:
                    print("    designations: {0}".format("\n      ".join(c
                        for c in bica_designations)))
                    print("    astro_object: {0}".format(astro_object))
                    print("    classifications: {0}".format("\n      ".join(c
                        for c in bica_classifications)))
                    print("    classifications: {0}".format(classifications))

                observations.append(
                    Observation(parameter=U,
                        value=combined[ref_code]["t4"][0]
                    )
                )
                observations.append(
                    Observation(parameter=V,
                        value=combined[ref_code]["t4"][1]
                    )
                )
                observations.append(
                    Observation(parameter=W,
                        value=combined[ref_code]["t4"][2]
                    )
                )

            # The point of Table2 seems to be Nobj, the number of relevant objects
            # in the reference. We do not add these data to Supaharris.
            if combined[ref_code]["t2"]:
                if verbose: print("\n  Found an entry in Table2")
                if debug: print("    {0}".format(combined[ref_code]["t2"]))

            # The point of Table3 seems to be GLON/GLAT, RA/DEC, Diam-a/Diam-b
            # for the 10978 entries in Bica+ 2019. We create Observation instances
            # for these six Parameter instances
            if combined[ref_code]["t3"]:
                if verbose: print("\n  Found an entry in Table3")
                if debug: print("    {0}".format(combined[ref_code]["t3"]))
                bica_classifications = combined[ref_code]["t3"][14] + combined[ref_code]["t3"][15]
                classifications = get_astro_object_classifications(bica_classifications)
                if verbose:
                    print("    bica_classifications: {0}".format("\n      ".join(c)
                        for c in bica_classifications))
                    print("    classifications: {0}".format(classifications))

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

