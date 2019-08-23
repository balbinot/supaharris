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

    fieldsets = (
        (None, {"fields": ( "id", )}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = (
        "title", "first_author", "year", "month", "journal",
        "doi", "volume", "pages"
    )
    search_fields = ( "first_author", "authors", "title", )
    readonly_fields = ( "slug", "bib_code" )
    list_filter = ( "year", "journal" )

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
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    ]

    def save_model(self, request, obj, form, change):
        # Here we sneak in the request when the model instance is changed.
        # This way we can pass a message to the request in the save method
        # of the model in case auto-retrieving data from the bibtex entry at
        # ADS failed.
        obj.request = request

        # And update the user who last updated the model instance
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AstroObjectClassification)
class AstroObjectClassificationAdmin(admin.ModelAdmin):
    list_display = ( "name", "abbreviation" )
    search_fields = ( "name", )
    readonly_fields = ( "slug", )

    fieldsets = (
        (None, {"fields": ("name", "abbreviation")}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AstroObject)
class AstroObjectAdmin(admin.ModelAdmin):
    list_display = ( "name", "altname", )
    list_filter = ("classifications",)
    search_fields = ( "name", "altname", )
    readonly_fields = ( "slug", )
    filter_horizontal = ( "classifications",)

    fieldsets = (
        (None, {"fields": ("name", "info")}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {"fields": ("name", "info")}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {"fields": ("name", "info")}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Auxiliary)
class AuxiliaryAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {"fields": ("name", "info")}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {"fields": ("name", "info")}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)
