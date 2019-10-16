from catalogue.models import Parameter
from catalogue.models import AstroObjectClassification


class PrepareSupaHarrisDatabaseMixin(object):
    def handle(self, *args, **options):
        print("Just making sure that your database has all required fixtures!")
        print_info = options.get("print_info")
        if "prin_info" in options.keys():
            options.pop("print_info")

        try:
            self.GC = AstroObjectClassification.objects.get(name="Globular Cluster")
        except AstroObjectClassification.DoesNotExist:
            print("\nWops, you forgot to load the AstroObjectClassification fixtures first!")
            print("But don't worry, we'll do this for you right now!")
            from django.core.management import call_command
            call_command("loaddata", "fixtures/catalogue_AstroObjectClassification")
            print("\nAll set.")

        try:
            Parameter.objects.get(name="RA")
        except Parameter.DoesNotExist:
            print("\nWops, you forgot to load the Parameter fixtures first!")
            print("But don't worry, we'll do this for you right now!")
            from django.core.management import call_command
            call_command("loaddata", "fixtures/catalogue_Parameter")
            print("\nAll set.")

        if print_info:
            print_parameters()
            print_astro_object_classifications()


def print_parameters():
    print("\n\n1) Below we print all parameters that are available in the ", end="")
    print("SupaHarris database. This will help you to figure out how ", end="")
    print("to 'convert' the parameters names in the database that you ",end="")
    print("would like to add to 'valid 'SupaHarris' parameter names.")

    print("\n  {0:<10s}{1:<10s}{2:<60s}{3:<12s}{4:<8s}".format(
        "id", "name", "description", "unit", "scale"))
    for p in Parameter.objects.all():
        print("  {0:<10d}{1:<10s}{2:<60s}{3:<12s}{4:<8.2f}".format(
            p.id, p.name, p.description, p.unit, p.scale))

    print("\nTo retrieve a specific parameter, use:\n")
    print("  `ra = Parameter.objects.get(name='RA')`, or")
    print("  `ra = Parameter.objects.get(id=1)`")


def print_astro_object_classifications():
    print("\n\n2) Below we print all object classification that are available ", end="")
    print("in the SupaHarris database.")

    print("\n  {0:<10s}{1:<50s}".format("id", "name"))
    for aoc in AstroObjectClassification.objects.all():
        print("  {0:<10d}{1:<50s}".format(aoc.id, aoc.name))

    print("To retrieve a specific object, use:\n\n")
    print("  `gc = AstroObjectClassification.objects.get(name='Globular Cluster')`, or")
    print("  `gc = AstroObjectClassification.objects.get(id=18)`")
