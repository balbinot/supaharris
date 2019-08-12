from django.shortcuts import render
from django.shortcuts import get_object_or_404

from catalogue.models import Reference
from catalogue.models import Parameter
from catalogue.models import Observation
from catalogue.models import AstroObject


def index(request):

    # Get the parameters we want to plot
    ra = Parameter.objects.get(name="RA")
    dec = Parameter.objects.get(name="Dec")
    l = Parameter.objects.get(name="L")
    b = Parameter.objects.get(name="B")

    # Get astro_objects that have observations of these parameters
    gcs_with_relevant_observations = Observation.objects.filter(
        parameter__in=[l, b, ra, dec]
    ).values('astro_object').distinct()
    astro_objects = AstroObject.objects.filter(id__in=gcs_with_relevant_observations)

    names = [o.name for o in astro_objects]
    ra = [c.observation_set.filter(parameter__name="RA") for c in astro_objects]
    dec = [c.observation_set.filter(parameter__name="Dec") for c in astro_objects]
    l_lon = [float(c.observation_set.get(parameter__name="L").value) for c in astro_objects]
    l_lon = [l if l < 180 else l - 360. for l in l_lon]
    b_lat = [float(c.observation_set.get(parameter__name="B").value) for c in astro_objects]

    # Plot the values we retrieved
    from bokeh.embed import components
    from bokeh.plotting import figure, ColumnDataSource

    source = ColumnDataSource(data=dict(
        x=l_lon,
        y=b_lat,
        names=names,
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
    return render(request, 'catalogue/search.html', {})


def reference_list(request):
    references = Reference.objects.all()
    return render(request, 'catalogue/reference_list.html',
        {'references': references})


def reference_detail(request, slug):
    reference = get_object_or_404(Reference, slug=slug)
    return render(request, 'catalogue/reference_detail.html',
        {"reference": reference})


def astro_object_list(request):
    astro_objects = AstroObject.objects.all()
    return render(request, 'catalogue/astro_object_list.html',
        {"astro_objects": astro_objects})


def astro_object_detail(request, slug):
    astro_object = get_object_or_404(AstroObject, slug=slug)
    return render(request, 'catalogue/astro_object_detail.html',
        {"astro_object": astro_object})

def parameter_list(request):
    parameters = Parameter.objects.all()
    return render(request, 'catalogue/parameter_list.html',
        {"parameters": parameters})

def parameter_detail(request, slug):
    parameter = get_object_or_404(Parameter, slug=slug)
    return render(request, 'catalogue/parameter_detail.html',
        {"parameter": parameter})

def observation_list(request):
    observations = Observation.objects.all()
    return render(request, 'catalogue/observation_list.html',
        {"observations": observations})


def observation_detail(request, slug):
    observation = get_object_or_404(Observation, slug=slug)
    return render(request, 'catalogue/observation_detail.html',
        {"observation": observation})
