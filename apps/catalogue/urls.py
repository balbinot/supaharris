from django.urls import path
from django.urls import re_path

from catalogue import views


app_name = "catalogue"  # namespace the urls
urlpatterns = [
    path("reference/list/", views.reference_list, name="reference_list"),
    path("reference/<slug>/", views.reference_detail, name="reference_detail"),
    path("cluster/list/", views.cluster_list, name="cluster_list"),
    path("cluster/<slug>/", views.cluster_detail, name="cluster_detail"),
    path("observation/list/", views.observation_list, name="observation_list"),
    path("observation/<pk>/", views.observation_detail, name="observaion_detail"),
]
