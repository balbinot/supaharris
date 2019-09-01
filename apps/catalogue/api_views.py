from rest_framework import viewsets
from rest_framework import filters
from rest_framework import generics
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from catalogue.models import (
    Reference,
    AstroObject,
    AstroObjectClassification,
    Parameter,
    Observation,
)
from catalogue.serializers import (
    ReferenceListSerializer,
    ReferenceDetailSerializer,
    AstroObjectListSerializer,
    AstroObjectDetailSerializer,
    AstroObjectClassificationSerializer,
    ParameterSerializer,
    ObservationSerializer,
)


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.order_by("id")
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ["first_author", "authors", "year", "title"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReferenceListSerializer
        if self.action == "retrieve":
            return ReferenceDetailSerializer
        return super().get_serializer_class()  # create/destroy/update

    @method_decorator(cache_page(15 * 60))  # 15 minutes
    def list(self, request, format=None):
        return super().list(request, format=format)


class AstroObjectClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AstroObjectClassification.objects.order_by("id")
    serializer_class = AstroObjectClassificationSerializer
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ["name",]

    @method_decorator(cache_page(15 * 60))  # 15 minutes
    def list(self, request, format=None):
        return super().list(request, format=format)


class AstroObjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AstroObject.objects.prefetch_related(
        "classifications",
        "observations", "observations__parameter", "observations__reference",
        "profiles", "auxiliaries",
    ).order_by("id")
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ["name", "altname", "classifications__name"]

    def get_serializer_class(self):
        if self.action == "list":
            return AstroObjectListSerializer
        if self.action == "retrieve":
            return AstroObjectDetailSerializer
        return super().get_serializer_class()  # create/destroy/update

    @method_decorator(cache_page(15 * 60))  # 15 minutes
    def list(self, request, format=None):
        return super().list(request, format=format)


class ParameterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parameter.objects.order_by("id")
    serializer_class = ParameterSerializer
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ["name", "description"]


    @method_decorator(cache_page(15 * 60))  # 15 minutes
    def list(self, request, format=None):
        return super().list(request, format=format)


class ObservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Observation.objects.select_related(
        "parameter", "reference", "astro_object",
    ).prefetch_related(
        "astro_object__classifications",
    ).order_by("id")
    serializer_class = ObservationSerializer
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "astro_object__name", "parameter__name", "value",
        # "reference__author", "reference__year", "reference__title",
    ]
    filterset_fields = ("astro_object", "parameter", "reference")

    @method_decorator(cache_page(15 * 60))  # 15 minutes
    def list(self, request, format=None):
        return super().list(request, format=format)
