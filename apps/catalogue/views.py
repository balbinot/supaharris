from django.shortcuts import render
from django.shortcuts import get_object_or_404

from catalogue.models import Reference
from catalogue.models import Observation
from catalogue.models import GlobularCluster


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
