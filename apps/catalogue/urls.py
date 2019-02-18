from django.urls import path
from django.urls import re_path

from catalogue import views


app_name = "catalogue"  # namespace the urls
urlpatterns = [
    path("", views.index, name="index"),
    path("cluster/", views.cluster_list, name="cluster_list"),
    path("cluster/<slug>", views.cluster_detail, name="cluster_detail"),
    path("references/", views.reference_list, name="reference_list"),
    path("references/<slug>", views.reference_detail, name="reference_detail"),
]
