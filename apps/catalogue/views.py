import numpy

from django.shortcuts import render
from django.shortcuts import get_object_or_404

from catalogue.models import (
    Reference,
    Parameter,
    Observation,
    AstroObject,
)


def index(request):
    # For now: Harris-only
    ads_url = "https://ui.adsabs.harvard.edu/abs/1996AJ....112.1487H"
    harris1996ed2010, created = Reference.objects.get_or_create(ads_url=ads_url)

    # Get the parameters we want to plot --> 4 queries
    p_ra = Parameter.objects.get(name="RA")
    p_dec = Parameter.objects.get(name="Dec")
    p_l = Parameter.objects.get(name="L")
    p_b = Parameter.objects.get(name="B")

    # Get astro_objects that have observations of these parameters
    relevant_astro_object_ids = list(set(Observation.objects.filter(
        parameter__in=[p_l, p_b, p_ra, p_dec]
    ).filter(
        reference=harris1996ed2010
    ).order_by("id").values_list("astro_object", flat=True)))
    astro_objects = AstroObject.objects.filter(
        id__in=relevant_astro_object_ids
    ).order_by("id")

    # Get relevant observations
    relevant_observations = numpy.array(
        Observation.objects.filter(
            parameter__in=[p_l, p_b, p_ra, p_dec], astro_object__in=astro_objects,
            reference=harris1996ed2010
        ).values_list(
            "astro_object__name", "parameter__name", "value", "sigma_up", "sigma_down",
        ).order_by("id"),
        dtype=[
            ("names", "S16"), ("parameter_names", "S16"), ("values", "float"),
            ("sigma_ups", "float"), ("sigma_downs", "float")
        ]
    )  # --> 5 columns, len(astro_objects) * 4 rows: ra, dec, l, b

    # Sanity check
    parameter_names = relevant_observations["parameter_names"][0:4]
    if len(parameter_names) < 1:
        import logging
        logger = logging.getLogger("request")
        logger.error("ERROR: no parameters in the database")
        return render(request, "catalogue/index.html", {
            "fig_script": None, "fig_div": None
        })
    if (parameter_names[0].decode("ascii") != "RA" or
            parameter_names[1].decode("ascii") != "Dec" or
            parameter_names[2].decode("ascii") != "L" or
            parameter_names[3].decode("ascii") != "B"):
        import logging
        logger = logging.getLogger("request")
        logger.error("ERROR: incorrect indices in index")
        return render(request, "catalogue/index.html", {
            "fig_script": None, "fig_div": None
        })

    names = relevant_observations["names"][::4]  # column /w astro_object__name
    ra, dec = relevant_observations["values"][0::4], relevant_observations["values"][1::4]
    l_lon, b_lat = relevant_observations["values"][2::4], relevant_observations["values"][3::4]
    l_lon = [l if l < 180 else l - 360. for l in l_lon]

    # Plot the values we retrieved
    from bokeh.embed import components
    from bokeh.plotting import figure, ColumnDataSource

    source = ColumnDataSource(data=dict(
        x=l_lon,
        y=b_lat,
        names=[n.decode("utf-8") for n in names],
    ))

    TOOLTIPS = [
        ("astro_object", "@names"),
        ("lon", "$x"),
        ("lat", "$y"),
    ]
    p = figure(width=600, height=300, sizing_mode="scale_width",
        tooltips=TOOLTIPS)

    p.circle("x", "y", source=source, color="red", fill_alpha=0.2, size=10)

    p.xaxis.axis_label = "Galactic Longitude [deg]"
    p.xaxis.axis_label_text_font_size = "18pt"
    p.xaxis.major_label_text_font_size = "14pt"

    p.yaxis.axis_label = "Galactic Latitude [deg]"
    p.yaxis.axis_label_text_font_size = "18pt"
    p.yaxis.major_label_text_font_size = "14pt"

    fig_script, fig_div = components(p)

    return render(request, "catalogue/index.html", {
        "fig_script": fig_script, "fig_div": fig_div
    })


def search(request):
    return render(request, "catalogue/search.html", {})


def reference_list(request):
    references = Reference.objects.all()
    date_updated = references.order_by("-date_updated").values_list("date_updated", flat=True).first()
    return render(request, "catalogue/reference_list.html",
        {"references": references, "date_updated": date_updated})


def reference_detail(request, slug):
    reference = get_object_or_404(Reference, slug=slug)
    return render(request, "catalogue/reference_detail.html",
        {"reference": reference})


def astro_object_list(request):
    astro_objects = AstroObject.objects.all()
    date_updated = astro_objects.order_by("-date_updated").values_list("date_updated", flat=True).first()
    return render(request, "catalogue/astro_object_list.html",
        {"astro_objects": astro_objects, "date_updated": date_updated})


def astro_object_detail(request, slug):
    astro_object = get_object_or_404(AstroObject, slug=slug)
    return render(request, "catalogue/astro_object_detail.html",
        {"astro_object": astro_object})


def parameter_list(request):
    parameters = Parameter.objects.all()
    date_updated = parameters.order_by("-date_updated").values_list("date_updated", flat=True).first()
    return render(request, "catalogue/parameter_list.html",
        {"parameters": parameters, "date_updated": date_updated})


def parameter_detail(request, slug):
    parameter = get_object_or_404(Parameter, slug=slug)
    return render(request, "catalogue/parameter_detail.html",
        {"parameter": parameter})


def observation_list(request):
    observations = Observation.objects.all()
    date_updated = observations.order_by("-date_updated").values_list("date_updated", flat=True).first()
    return render(request, "catalogue/observation_list.html",
        {"observations": observations, "date_updated": date_updated})


def observation_detail(request, slug):
    observation = get_object_or_404(Observation, slug=slug)
    return render(request, "catalogue/observation_detail.html",
        {"observation": observation})
