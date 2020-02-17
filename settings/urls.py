from django.urls import path
from django.urls import include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from filebrowser.sites import site
from rest_framework import routers

from catalogue.views import index
from catalogue import api_views as catalogue_api


handler404 = "about.views.handler404"
handler500 = "about.views.handler500"

router = routers.DefaultRouter()
router.register(r"catalogue/reference", catalogue_api.ReferenceViewSet)
router.register(r"catalogue/astro_object", catalogue_api.AstroObjectViewSet)
router.register(r"catalogue/astro_object_classifcation", catalogue_api.AstroObjectClassificationViewSet)
router.register(r"catalogue/parameter", catalogue_api.ParameterViewSet)
router.register(r"catalogue/observation", catalogue_api.ObservationViewSet)
router.register(r"catalogue/observation_table", catalogue_api.ObservationTableViewset, basename="observation_table")

urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path("admin/", admin.site.urls),
    path("admin/password_reset/", auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",),
    path("admin/", include("django.contrib.auth.urls")),
    path("admin/silk/", include("silk.urls", namespace="silk")),

    path("tinymce/", include("tinymce.urls")),
    path("api/v1/auth/", include("rest_framework.urls")),
    path("api/v1/", include(router.urls)),

    path("", index, name="index"),
    path("about/", include("about.urls")),
    path("accounts/", include("accounts.urls")),
    path("catalogue/", include("catalogue.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
