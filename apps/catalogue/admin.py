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
from catalogue.filters import DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ( "name", "description", "unit", "scale" )
    search_fields = ( "name", "description", )
    readonly_fields = (
        "slug", "date_created", "date_updated", "last_updated_by",
    )

    fieldsets = (
        (None, {"fields": ( "name", "description", "unit", "scale", )}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "slug", "date_created", "date_updated", "last_updated_by" )
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
    readonly_fields = (
        "slug", "bib_code", "date_created", "date_updated", "last_updated_by",
    )
    list_filter = (
        ("year", DropdownFilter),
        ("journal", ChoiceDropdownFilter),
    )

    fieldsets = [
        ("Required", {
            "fields": [ "ads_url", "bib_code" ]
        }),
        ("Automatically retrieved!", {
            "fields": [
                "title", "first_author", "authors", "journal", "doi",
                "year", "month", "volume", "pages",
            ]
        }),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "slug", "date_created", "date_updated", "last_updated_by" )
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
    readonly_fields = (
        "slug", "date_created", "date_updated", "last_updated_by",
    )

    fieldsets = (
        (None, {"fields": ( "name", "abbreviation" )}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "slug", "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AstroObject)
class AstroObjectAdmin(admin.ModelAdmin):
    list_display = ( "name", "altname", )
    list_filter = (
        ("classifications", RelatedDropdownFilter),
    )
    search_fields = ( "name", "altname", )
    readonly_fields = (
        "slug", "date_created", "date_updated", "last_updated_by",
    )
    filter_horizontal = ( "classifications",)

    fieldsets = (
        (None, {"fields": ( "name", "altname", "classifications", )}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "slug", "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    autocomplete_fields = ( "astro_object", "parameter", "reference", )
    search_fields = ( "astro_object", "parameter", "reference", )
    readonly_fields = (
        "date_created", "date_updated", "last_updated_by",
    )

    fieldsets = (
        (None, {"fields": (
            "astro_object", "parameter",
            "value", "sigma_up", "sigma_down",
            "reference",
            )
        }),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "reference", "astro_object", "parameter",
        )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    autocomplete_fields = ( "observation", )
    search_fields = ( "observation", )
    readonly_fields = (
        "date_created", "date_updated", "last_updated_by",
    )

    fieldsets = (
        (None, {"fields": ( "observation", "rank", "weight", "compilation_name" )}),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "observation",
        )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Auxiliary)
class AuxiliaryAdmin(admin.ModelAdmin):
    autocomplete_fields = ( "astro_object", "reference", )
    search_fields = ( "astro_object", "reference", )
    readonly_fields = (
        "date_created", "date_updated", "last_updated_by",
    )

    fieldsets = (
        (None, {"fields": ( "astro_object", "path", "url", "reference", )}),
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
    autocomplete_fields = ( "astro_object", "reference", )
    search_fields = ( "astro_object", "reference", )
    readonly_fields = (
        "date_created", "date_updated", "last_updated_by",
    )

    fieldsets = (
        (None, {"fields": (
            "astro_object",
            "profile_type", "profile", "model_parameters", "model_flavour",
            "reference",
            )
        }),
        ("Meta", {
            "classes": ("collapse",),
            "fields": ( "date_created", "date_updated", "last_updated_by" )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "reference", "astro_object",
        )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)
