import pandas as pd

from django.shortcuts import render
from django.shortcuts import get_object_or_404

from catalogue.models import Reference
from catalogue.models import Parameter
from catalogue.models import Observation
from catalogue.models import GlobularCluster


def index(request):

    # Get the parameters we want to plot
    ra = Parameter.objects.get(name="RA")
    dec = Parameter.objects.get(name="Dec")
    l = Parameter.objects.get(name="L")
    b = Parameter.objects.get(name="B")

    # Get clusters that have observations of these parameters
    gcs_with_relevant_observations = Observation.objects.filter(
        parameter__in=[l, b, ra, dec]
    ).values('cluster').distinct()
    clusters = GlobularCluster.objects.filter(id__in=gcs_with_relevant_observations)

    names = pd.Series([o.name for o in clusters])
    ra = pd.Series([c.observation_set.filter(parameter__name="RA") for c in clusters])
    dec = pd.Series([c.observation_set.filter(parameter__name="Dec") for c in clusters])
    l_lon = pd.Series([float(c.observation_set.get(parameter__name="L").value) for c in clusters])
    b_lat = pd.Series([float(c.observation_set.get(parameter__name="B").value) for c in clusters])
    l_lon[l_lon > 180] = l_lon[l_lon > 180] - 360.

    # Plot the values we retrieved
    from bokeh.plotting import figure, ColumnDataSource
    from bokeh.embed import components

    source = ColumnDataSource(data=dict(
        x=l_lon,
        y=b_lat,
        names=names,
    ))

    TOOLTIPS = [
        ("Cluster", "@names"),
        ("lon", "$x"),
        ("lat", "$y"),
    ]
    p = figure(title="Globular Clusters", tooltips=TOOLTIPS)
    p.xaxis.axis_label = "Galactic Longitude [deg]"
    p.yaxis.axis_label = "Galactic Latitude [deg]"
    p.circle("x", "y", source=source, color="red", fill_alpha=0.2, size=10)
    fig_script, fig_div = components(p)

    return render(request, "catalogue/index.html", {
        "fig_script": fig_script, "fig_div": fig_div
    })



def reference_list(request):
    references = Reference.objects.all()
    return render(request, 'catalogue/reference_list.html',
        {'references': references})


def reference_detail(request, slug):
    reference = get_object_or_404(Reference, slug=slug)
    return render(request, 'catalogue/reference_detail.html',
        {"reference": reference})


def cluster_list(request):
    clusters = GlobularCluster.objects.all()
    return render(request, 'catalogue/cluster_list.html',
        {"clusters": clusters})


def cluster_detail(request, slug):
    cluster = get_object_or_404(GlobularCluster, slug=slug)
    return render(request, 'catalogue/cluster_detail.html',
        {"cluster": cluster})

def observation_list(request):
    observations = Observation.objects.all()
    return render(request, 'catalogue/observation_list.html',
        {"observations": observations})


def observation_detail(request, slug):
    observation = get_object_or_404(Observation, pk=pk)
    return render(request, 'catalogue/observation_detail.html',
        {"observation": observation})
