from django.contrib import admin

from catalogue.models import Parameter
from catalogue.models import Reference
from catalogue.models import GlobularCluster
from catalogue.models import Observation
from catalogue.models import Rank
from catalogue.models import Auxiliary
from catalogue.models import Profile

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ( "name", "description", "unit", "scale", "slug" )
    readonly_fields = ( "slug", )


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = (
        "title", "first_author", "year", "month", "journal",
        "doi", "volume", "pages"
    )
    search_fields = ( "first_author", "authors", "title", )
    readonly_fields = ( "slug", )
    list_filter = ( "year", "journal" )
    fieldsets = [
        ("Required", {
            "fields": [ "ads_url", ]
        }),
        ("Automatically Retrieved!", {
            "fields": [
                "first_author", "authors", "journal", "doi",
                "year", "month", "volume", "pages",
            ]
        }),
    ]


@admin.register(GlobularCluster)
class GlobularClusterAdmin(admin.ModelAdmin):
    list_display = ( "name", "altname", )
    search_fields = ( "name", "altname", )
    readonly_fields = ( "slug", )


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    pass


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    pass


@admin.register(Auxiliary)
class AuxiliaryAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
