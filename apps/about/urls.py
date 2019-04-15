from django.urls import path

from about import views


app_name = "about"  # namespace the urls
urlpatterns = [
    path(r"info/", views.info, name="info"),
    path(r"privacy_policy/", views.privacy_policy, name="privacy_policy"),
]
