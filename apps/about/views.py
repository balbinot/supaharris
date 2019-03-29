import numpy as np
from matplotlib import pyplot as plt

from django.shortcuts import render
from django.shortcuts import get_object_or_404

from catalogue.models import Reference
from catalogue.models import Observation
from catalogue.models import GlobularCluster


def index(request):
    harris1996ed2010 = get_object_or_404(Reference, bib_code="1996AJ....112.1487H")
    # clusters = GlobularCluster.objects.filter(references=harris1996ed2010)
    clusters = GlobularCluster.objects.all()
    names = np.array([o.name for o in clusters])
    ra = np.array([c.observation_set.filter(parameter__name="RA") for c in clusters])
    dec = np.array([c.observation_set.filter(parameter__name="Dec") for c in clusters])
    l = np.array([c.observation_set.filter(parameter__name="L") for c in clusters])
    b = np.array([c.observation_set.filter(parameter__name="B") for c in clusters])
    # urls = ["cluster/"+o.name for o in cs]
    # l[l>180] = l[l>180] - 360.

    from bokeh.plotting import figure, show, output_file
    from bokeh.sampledata.iris import flowers
    from bokeh.embed import components

    colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
    colors = [colormap[x] for x in flowers['species']]

    p = figure(title = "Iris Morphology")
    p.xaxis.axis_label = 'Petal Length'
    p.yaxis.axis_label = 'Petal Width'
    p.circle(flowers["petal_length"], flowers["petal_width"],
             color=colors, fill_alpha=0.2, size=10)
    fig_script, fig_div = components(p)

    return render(request, "about/index.html", {
        "fig_script": fig_script, "fig_div": fig_div})


def info(request):
    return render(request, "about/info.html", {})

def privacy_policy(request):
    return render(request, "about/privacy_policy.html", {})

def page_not_found(request):
    return render(request, "404.html")
