from django.contrib import admin

from catalogue.models import (
    Parameter,
    Reference,
    AstroObject,
    AstroObjectClassification,
    Observation,
    Rank,
    Auxiliary,
    Profile,
)


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
    readonly_fields = ( "slug", "bib_code" )
    list_filter = ( "year", "journal" )
    # autocomplete_fields = ( "astro_objects", )
    filter_horizontal = ( "astro_objects", )

    fieldsets = [
        ("Required", {
            "fields": [ "ads_url", "bib_code" ]
        }),
        ("Automatically Retrieved!", {
            "fields": [
                "title", "first_author", "authors", "journal", "doi",
                "year", "month", "volume", "pages",
            ]
        }),
        ("Relations", {
            "fields": [
                "astro_objects",
            ]
        }),
    ]

    def save_model(self, request, obj, form, change):
        # Here we sneak in the request when the model instance is changed.
        # This way we can pass a message to the request in the save method
        # of the model in case auto-retrieving data from the bibtex entry at
        # ADS failed.
        obj.request = request
        super().save_model(request, obj, form, change)


@admin.register(AstroObjectClassification)
class AstroObjectClassificationAdmin(admin.ModelAdmin):
    list_display = ( "name", )
    search_fields = ( "name", )
    readonly_fields = ( "slug", )


@admin.register(AstroObject)
class AstroObjectAdmin(admin.ModelAdmin):
    list_display = ( "name", "altname", )
    search_fields = ( "name", "altname", )
    readonly_fields = ( "slug", )
    filter_horizontal = ( "classification",)


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
