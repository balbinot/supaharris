from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter,
    RelatedOnlyFieldListFilter,
)


# https://github.com/mrts/django-admin-list-filter-dropdown/
class DropdownFilter(AllValuesFieldListFilter):
    template = "catalogue/dropdown_filter.html"


class ChoiceDropdownFilter(ChoicesFieldListFilter):
    template = "catalogue/dropdown_filter.html"


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = "catalogue/dropdown_filter.html"


class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    template = "catalogue/dropdown_filter.html"
