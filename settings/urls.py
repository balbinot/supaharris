from django.urls import path
from django.urls import include
from django.conf import settings
from django.contrib import admin
from django.conf.urls import handler404
from django.conf.urls.static import static

from filebrowser.sites import site

from catalogue.views import index

handler404 = "about.views.page_not_found"
handler500 = handler404


urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),

    path("", index, name="index"),
    path("about/", include("about.urls")),
    path("account/", include("accounts.urls")),
    path("catalogue/", include("catalogue.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
