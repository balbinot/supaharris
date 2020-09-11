from catalogue import views
from django.urls import path, re_path

app_name = "catalogue"  # namespace the urls
urlpatterns = [
    path("search/", views.search, name="search"),
    path("reference/list/", views.reference_list, name="reference_list"),
    path("reference/<slug>/", views.reference_detail, name="reference_detail"),
    path("astro_object/list/", views.astro_object_list, name="astro_object_list"),
    path("astro_object/<slug>/", views.astro_object_detail, name="astro_object_detail"),
    path("parameter/list/", views.parameter_list, name="parameter_list"),
    path("parameter/<slug>/", views.parameter_detail, name="parameter_detail"),
    path("observation/list/", views.observation_list, name="observation_list"),
    path("observation/<pk>/", views.observation_detail, name="observaion_detail"),
]
