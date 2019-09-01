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
    # Get the parameters we want to plot --> 4 queries
    p_ra = Parameter.objects.get(name="RA")
    p_dec = Parameter.objects.get(name="Dec")
    p_l = Parameter.objects.get(name="L")
    p_b = Parameter.objects.get(name="B")

    # Get astro_objects that have observations of these parameters
    gcs_with_relevant_observations = Observation.objects.select_related(
        "parameter",  # 1 query w join
    ).filter(
        parameter__in=[p_l, p_b, p_ra, p_dec]
    ).values("astro_object").distinct()  # 1 query

    astro_objects = AstroObject.objects.prefetch_related(
        "classifications", "observations", "observations__parameter",  # 3 queries
    ).filter(
        id__in=gcs_with_relevant_observations
    )  # 1 query

    N = astro_objects.count()  # 1 query
    names = numpy.zeros(N, dtype="S64")
    ra, dec = numpy.zeros(N), numpy.zeros(N)
    l_lon, b_lat = numpy.zeros(N), numpy.zeros(N)
    for i, o in enumerate(astro_objects.iterator()):
        names[i] = str(o.name)
        ra[i] = o.observations.get(parameter=p_ra).value
        dec[i] = o.observations.get(parameter=p_dec).value
        l_lon[i] = float(o.observations.get(parameter=p_l).value)
        b_lat[i] = float(o.observations.get(parameter=p_b).value)

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
    return render(request, "catalogue/reference_list.html",
        {"references": references})


def reference_detail(request, slug):
    reference = get_object_or_404(Reference, slug=slug)
    return render(request, "catalogue/reference_detail.html",
        {"reference": reference})


def astro_object_list(request):
    astro_objects = AstroObject.objects.all()
    return render(request, "catalogue/astro_object_list.html",
        {"astro_objects": astro_objects})


def astro_object_detail(request, slug):
    astro_object = get_object_or_404(AstroObject, slug=slug)
    return render(request, "catalogue/astro_object_detail.html",
        {"astro_object": astro_object})

def parameter_list(request):
    parameters = Parameter.objects.all()
    return render(request, "catalogue/parameter_list.html",
        {"parameters": parameters})

def parameter_detail(request, slug):
    parameter = get_object_or_404(Parameter, slug=slug)
    return render(request, "catalogue/parameter_detail.html",
        {"parameter": parameter})

def observation_list(request):
    observations = Observation.objects.all()
    return render(request, "catalogue/observation_list.html",
        {"observations": observations})


def observation_detail(request, slug):
    observation = get_object_or_404(Observation, slug=slug)
    return render(request, "catalogue/observation_detail.html",
        {"observation": observation})
