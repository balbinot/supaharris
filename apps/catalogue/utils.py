from catalogue.models import Parameter


def get_parameter_names_from_supaharris():
    print("Below we print all parameters that are available in the ", end="")
    print("SupaHarris database. This will help you to figure out how ", end="")
    print("to 'convert' the parameters names in the database that you ",end="")
    print("would like to add to 'valid 'SupaHarris' parameter names.")

    available_parameters = Parameter.objects.all()

    print("\n{0:<10s}{1:<50s}{2:<12s}{3:<8s}".format(
        "name", "description", "unit", "scale"))
    for p in available_parameters:
        print("{0:<10s}{1:<50s}{2:<12s}{3:<8.2f}".format(
            p.name, p.description, p.unit, p.scale))
