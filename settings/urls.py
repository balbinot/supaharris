from django.urls import path
from django.urls import include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

from filebrowser.sites import site


urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path(r"admin/", admin.site.urls),
    path(r'tinymce/', include('tinymce.urls')),
    path(r"", include("about.urls")),
    path(r"catalogue/", include("catalogue.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
