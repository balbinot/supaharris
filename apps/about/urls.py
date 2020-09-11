from about import views
from django.urls import path

app_name = "about"  # namespace the urls
urlpatterns = [
    path(r"info/", views.info, name="info"),
    path(r"privacy_policy/", views.privacy_policy, name="privacy_policy"),
]
