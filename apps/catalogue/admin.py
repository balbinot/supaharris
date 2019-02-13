from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from catalogue.models import GlobularCluster
from catalogue.models import Observation
from catalogue.models import Reference
from catalogue.models import Parameter
from catalogue.models import Rank
from catalogue.models import Auxiliary
from catalogue.models import Profile


@admin.register(Reference)
class Referencedmin(admin.ModelAdmin):
    list_display = (
        "title", "first_author", "year", "month", "journal",
        "doi", "volume", "pages"
    )
    search_fields = ( "first_author", "authors", "title", )
    readonly_fields = ( "slug", )
    list_filter = ( "year", "journal" )
    fieldsets = [
        (_("Required"), {
            "fields": [ "ads_url", ]
        }),
        (_("Automatically Retrieved!"), {
            "fields": [
                "first_author", "authors", "journal", "doi",
                "year", "month", "volume", "pages",
            ]
        }),
    ]



admin.site.register(GlobularCluster)
admin.site.register(Observation)
admin.site.register(Parameter)
admin.site.register(Rank)
admin.site.register(Auxiliary)
admin.site.register(Profile)
