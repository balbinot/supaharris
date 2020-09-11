import logging

from catalogue.models import AstroObject, AstroObjectClassification, Parameter
from utils import convert_gc_names_from_sh_to_any


class PrepareSupaHarrisDatabaseMixin(object):
    def handle(self, *args, **options):
        # Verbosity level; 0=minimal output, 1=normal output,
        # 2=verbose output, 3=very verbose output
        self.verbosity = int(options["verbosity"])
        self.logger = logging.getLogger()
        self.logger.propagate = False
        self.logger.level = logging.DEBUG
        for h in self.logger.handlers:
            h.setLevel(self.logger.level)
            h.setFormatter(logging.Formatter("%(message)s"))

        self.logger.debug(
            "PrepareSupaHarrisDatabaseMixin: making sure that your"
            + " database has all required fixtures!"
        )
        try:
            self.GC = AstroObjectClassification.objects.get(name="Globular Cluster")
            assert self.GC.id == 18, (
                "Incorrect id for AstroObjectClassification"
                + " 'Globular Cluster', expected 18 but found {0}".format(self.GC.id)
            )
        except AstroObjectClassification.DoesNotExist:
            self.logger.warning(
                "\nWops, you forgot to load the AstroObjectClassification fixtures first!"
            )
            self.logger.warning("But don't worry, we'll do this for you right now!")
            from django.core.management import call_command

            call_command("loaddata", "fixtures/catalogue_AstroObjectClassification")
            self.logger.warning("\nAll set.")

        try:
            ra = Parameter.objects.get(name="RA")
            assert ra.id == 1, (
                "Incorrect id for Parameter"
                + " 'RA', expected 1 but found {0}".format(ra.id)
            )
        except Parameter.DoesNotExist:
            self.logger.warning(
                "\nWops, you forgot to load the Parameter fixtures first!"
            )
            self.logger.warning("But don't worry, we'll do this for you right now!")
            from django.core.management import call_command

            call_command("loaddata", "fixtures/catalogue_Parameter")
            self.logger.warning("\nAll set.")

        if (
            self.verbosity >= 1
        ):  # verbosity = {1: normal, 2: verbose, and 3: very verbose}
            print_parameters(self.logger)
            print_astro_object_classifications(self.logger)


def print_parameters(logger):
    logger.info("\n\n1) Below we print all parameters that are available in the")
    logger.info("SupaHarris database. This will help you to figure out how")
    logger.info("to 'convert' the parameters names in the database that you")
    logger.info("would like to add to 'valid 'SupaHarris' parameter names.")

    logger.info(
        "\n  {0:<10s}{1:<20s}{2:<60s}{3:<15s}{4:<8s}".format(
            "id", "name", "description", "unit", "scale"
        )
    )
    for p in Parameter.objects.all():
        logger.info(
            "  {0:<10d}{1:<20s}{2:<60s}{3:<15s}{4:<8.2f}".format(
                p.id,
                p.name,
                p.description[:55] + ("" if len(p.description) < 55 else ".."),
                p.unit,
                p.scale,
            )
        )

    logger.info("\nTo retrieve a specific parameter, use:\n")
    logger.info("  `ra = Parameter.objects.get(name='RA')`, or")
    logger.info("  `ra = Parameter.objects.get(id=1)`")
    logger.info("-" * 80)


def print_astro_object_classifications(logger):
    logger.info("\n\n2) Below we print all object classification that are available")
    logger.info("in the SupaHarris database.")

    logger.info("\n  {0:<10s}{1:<50s}".format("id", "name"))
    for aoc in AstroObjectClassification.objects.all():
        logger.info("  {0:<10d}{1:<50s}".format(aoc.id, aoc.name))

    logger.info("\nTo retrieve a specific object, use:\n\n")
    logger.info(
        "  `gc = AstroObjectClassification.objects.get(name='Globular Cluster')`, or"
    )
    logger.info("  `gc = AstroObjectClassification.objects.get(id=18)`")
    logger.info("-" * 80)


def map_names_to_ids():
    names = dict()
    for ao in AstroObject.objects.iterator():
        names[ao.name] = ao.id
        for v in convert_gc_names_from_sh_to_any(ao.name):
            names[v] = ao.id

        if ao.altname:
            names[ao.altname] = ao.id
            for v in convert_gc_names_from_sh_to_any(ao.altname):
                names[v] = ao.id

    return names
