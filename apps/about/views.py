import pandas as pd
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from catalogue.models import Reference
from catalogue.models import Observation
from catalogue.models import GlobularCluster


def index(request):
    harris1996ed2010 = get_object_or_404(Reference, bib_code="1996AJ....112.1487H")
    # clusters = GlobularCluster.objects.filter(references=harris1996ed2010)
    clusters = GlobularCluster.objects.all()
    names = pd.Series([o.name for o in clusters])
    ra = pd.Series([c.observation_set.filter(parameter__name="RA") for c in clusters])
    dec = pd.Series([c.observation_set.filter(parameter__name="Dec") for c in clusters])
    # TODO: how to handle if GlobularCluster has no Observation of Parameter L?
    l_lon = pd.Series([float(c.observation_set.get(parameter__name="L").value) for c in clusters])
    b_lat = pd.Series([float(c.observation_set.get(parameter__name="B").value) for c in clusters])
    # urls = ["cluster/"+o.name for o in cs]
    l_lon[l_lon > 180] = l_lon[l_lon > 180] - 360.

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

    return render(request, "about/index.html", {
        "fig_script": fig_script, "fig_div": fig_div
    })


def info(request):
    return render(request, "about/info.html", {})

def privacy_policy(request):
    return render(request, "about/privacy_policy.html", {})

def page_not_found(request):
    return render(request, "404.html")
