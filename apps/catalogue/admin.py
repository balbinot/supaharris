from catalogue.filters import (
    ChoiceDropdownFilter,
    DropdownFilter,
    RelatedDropdownFilter,
)
from catalogue.models import (
    AstroObject,
    AstroObjectClassification,
    Auxiliary,
    Observation,
    Parameter,
    Profile,
    Rank,
    Reference,
)
from django.contrib import admin


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "unit", "scale")
    search_fields = (
        "name",
        "description",
    )
    readonly_fields = (
        "slug",
        "date_created",
        "date_updated",
        "last_updated_by",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "unit",
                    "scale",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("slug", "date_created", "date_updated", "last_updated_by"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "first_author",
        "year",
        "month",
        "journal",
        "doi",
        "volume",
        "pages",
    )
    search_fields = (
        "first_author",
        "authors",
        "title",
        "bib_code",
        "ads_url",
    )
    readonly_fields = (
        "slug",
        "bib_code",
        "date_created",
        "date_updated",
        "last_updated_by",
    )
    list_filter = (
        ("year", DropdownFilter),
        ("journal", ChoiceDropdownFilter),
    )

    fieldsets = [
        ("Required", {"fields": ["ads_url", "bib_code"]}),
        (
            "Automatically retrieved!",
            {
                "fields": [
                    "title",
                    "first_author",
                    "authors",
                    "journal",
                    "doi",
                    "year",
                    "month",
                    "volume",
                    "pages",
                ]
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("slug", "date_created", "date_updated", "last_updated_by"),
            },
        ),
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
    list_display = ("name", "abbreviation")
    search_fields = ("name",)
    readonly_fields = (
        "slug",
        "date_created",
        "date_updated",
        "last_updated_by",
    )

    fieldsets = (
        (None, {"fields": ("name", "abbreviation")}),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("slug", "date_created", "date_updated", "last_updated_by"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AstroObject)
class AstroObjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "altname",
    )
    list_filter = (("classifications", RelatedDropdownFilter),)
    search_fields = (
        "name",
        "altname",
    )
    readonly_fields = (
        "slug",
        "date_created",
        "date_updated",
        "last_updated_by",
    )
    filter_horizontal = ("classifications",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "altname",
                    "classifications",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("slug", "date_created", "date_updated", "last_updated_by"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "astro_object",
        "parameter",
        "reference",
    )
    search_fields = (
        "astro_object",
        "parameter",
        "reference",
    )
    readonly_fields = (
        "date_created",
        "date_updated",
        "last_updated_by",
    )
    list_filter = (
        ("astro_object", RelatedDropdownFilter),
        ("parameter", RelatedDropdownFilter),
        ("reference", RelatedDropdownFilter),
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "astro_object",
                    "parameter",
                    "value",
                    "sigma_up",
                    "sigma_down",
                    "reference",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("date_created", "date_updated", "last_updated_by"),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "reference",
                "astro_object",
                "parameter",
            )
        )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    autocomplete_fields = ("observation",)
    search_fields = ("observation",)
    readonly_fields = (
        "date_created",
        "date_updated",
        "last_updated_by",
    )

    fieldsets = (
        (None, {"fields": ("observation", "rank", "weight", "compilation_name")}),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("date_created", "date_updated", "last_updated_by"),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "observation",
            )
        )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Auxiliary)
class AuxiliaryAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "astro_object",
        "reference",
    )
    search_fields = (
        "astro_object",
        "reference",
    )
    readonly_fields = (
        "date_created",
        "date_updated",
        "last_updated_by",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "astro_object",
                    "reference",
                    "description",
                    "file",
                    "url",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("date_created", "date_updated", "last_updated_by"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("get_name", "astro_object", "reference", "get_len_x", "get_len_y")
    autocomplete_fields = (
        "astro_object",
        "reference",
    )
    search_fields = (
        "astro_object",
        "reference",
    )
    readonly_fields = (
        "date_created",
        "date_updated",
        "last_updated_by",
    )
    list_filter = (
        ("astro_object", RelatedDropdownFilter),
        ("reference", RelatedDropdownFilter),
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "astro_object",
                    "reference",
                    "x",
                    "x_description",
                    "y",
                    "y_description",
                    "y_sigma_up",
                    "y_sigma_down",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("date_created", "date_updated", "last_updated_by"),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "reference",
                "astro_object",
            )
        )

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    def get_name(self, obj):
        return "{} vs {}".format(obj.y_description, obj.x_description)

    get_name.short_description = "Profile"

    def get_len_x(self, obj):
        return len(obj.x)

    get_len_x.short_description = "len(x)"
    # TODO: annotate the qs /w len_x?
    # get_len_x.admin_order_field = "len_x"

    def get_len_y(self, obj):
        return len(obj.y)

    get_len_y.short_description = "len(y)"
    # get_len_y.admin_order_field = "len_y"
