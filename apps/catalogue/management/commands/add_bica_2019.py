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


def create_references_for_bica_references(debug=True):
    references = list()
    bica_references = parse_bica_2019_refs()
    nrefs = len(bica_references)
    for i, (ref_code, [ref, bib_code, cat]) in enumerate(bica_references.items()):
        if debug:
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
            setattr(Reference, ref_code, reference)
            references.append(ref_code)
        else:
            reference, created = Reference.objects.get_or_create(ads_url=ads_url)
            setattr(Reference, ref_code, reference)
            references.append(ref_code)

        if not created:
            if debug: print("Found the Reference: {0}\n".format(ref_code))
        else:
            if debug: print("Created the Reference: {0}\n".format(ref_code))
    return references


def combine_tables(debug=True):
    t2 = parse_bica_2019_table2(debug=debug)
    t3 = parse_bica_2019_table3(debug=debug)
    t4 = parse_bica_2019_table4(debug=debug)
    t5 = parse_bica_2019_table5(debug=debug)

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

        # Parse and get or create Reference instances for refs.dat
        references = create_references_for_bica_references(debug=False)
        print("INFO: found {0} references".format(len(references)))
        combined = combine_tables(debug=False)
        print("INFO: found {0} references in the combined tables".format(len(combined)))
        unknown_references = [k for k in combined.keys() if k not in references]
        print("WARNING: found {0} unknown_references".format(len(unknown_references)))


        # TODO: match the four Bica+ 2019 tables, add AstroObject and Observation instances
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

