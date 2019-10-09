from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

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
    ObservationTableSerializer,
)


class ReferenceViewSet(ReadOnlyModelViewSet):
    queryset = Reference.objects.order_by("id")
    filter_backends = [
        DatatablesFilterBackend,
        SearchFilter,
    ]
    search_fields = ["first_author", "authors", "year", "title"]

    # Make url parameter 'length' work for all renderers
    DatatablesPageNumberPagination.page_size_query_param = "length"

    def get_serializer_class(self):
        if self.action == "list":
            return ReferenceListSerializer
        if self.action == "retrieve":
            return ReferenceDetailSerializer
        return ReferenceListSerializer   # head/create/destroy/update

    @method_decorator(cache_page(4 * 3600))  # 4 hours
    def list(self, request, format=None):
        return super().list(request, format=format)


class AstroObjectClassificationViewSet(ReadOnlyModelViewSet):
    queryset = AstroObjectClassification.objects.order_by("id")
    serializer_class = AstroObjectClassificationSerializer
    filter_backends = [
        DatatablesFilterBackend,
        SearchFilter,
    ]
    search_fields = ["name",]

    # Make url parameter 'length' work for all renderers
    DatatablesPageNumberPagination.page_size_query_param = "length"

    @method_decorator(cache_page(4 * 3600))  # 4 hours
    def list(self, request, format=None):
        return super().list(request, format=format)


class AstroObjectViewSet(ReadOnlyModelViewSet):
    queryset = AstroObject.objects.prefetch_related(
        "classifications",
        "observations", "observations__parameter", "observations__reference",
        "profiles", "auxiliaries",
    ).order_by("id")
    filter_backends = [
        DatatablesFilterBackend,
        SearchFilter,
    ]
    search_fields = ["name", "altname", "classifications__name"]

    # Make url parameter 'length' work for all renderers
    DatatablesPageNumberPagination.page_size_query_param = "length"

    def get_serializer_class(self):
        if self.action == "list":
            return AstroObjectListSerializer
        if self.action == "retrieve":
            return AstroObjectDetailSerializer
        return AstroObjectListSerializer  # head/create/destroy/update

    @method_decorator(cache_page(4 * 3600))  # 4 hours
    def list(self, request, format=None):
        return super().list(request, format=format)


class ParameterViewSet(ReadOnlyModelViewSet):
    queryset = Parameter.objects.order_by("id")
    serializer_class = ParameterSerializer
    filter_backends = [
        DatatablesFilterBackend,
        SearchFilter,
    ]
    search_fields = ["name", "description"]

    # Make url parameter 'length' work for all renderers
    DatatablesPageNumberPagination.page_size_query_param = "length"


    @method_decorator(cache_page(4 * 3600))  # 4 hours
    def list(self, request, format=None):
        return super().list(request, format=format)


class ObservationViewSet(ReadOnlyModelViewSet):
    queryset = Observation.objects.select_related(
        "parameter", "reference", "astro_object",
    ).prefetch_related(
        "astro_object__classifications",
    ).order_by("id")
    serializer_class = ObservationSerializer
    filter_backends = [
        DatatablesFilterBackend,
        SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "astro_object__name", "parameter__name", "value",
        # "reference__author", "reference__year", "reference__title",
    ]
    filterset_fields = ("astro_object", "parameter", "reference")

    # Make url parameter 'length' work for all renderers
    DatatablesPageNumberPagination.page_size_query_param = "length"

    @method_decorator(cache_page(4 * 3600))  # 4 hours
    def list(self, request, format=None):
        return super().list(request, format=format)


class ObservationTable(object):
    def __init__(self, row, **kwargs):
        for k, v in row.items():
            setattr(self, k, v)


class ObservationTableViewset(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = ObservationTableSerializer
    filter_backends = [
        DatatablesFilterBackend,
        DjangoFilterBackend,
    ]
    filterset_fields = ("reference",)

    def list(self, request):
        data = {}

        h96 = Reference.objects.get(bib_code="1996AJ....112.1487H")
        relevant_observations = Observation.objects.filter(
            reference=h96,
        ).select_related(
            "parameter", "reference", "astro_object",
        ).prefetch_related(
            "astro_object__classifications",
        ).order_by("id")

        parameters = relevant_observations.order_by(
            "parameter__id"
        ).values(
            "parameter__id", "parameter__name"
        ).distinct()
        parameter_names = [p["parameter__name"] for p in parameters]
        print("This reference has {0} parameters".format(parameters.count()))

        astro_objects = relevant_observations.order_by(
            "astro_object__id"
        ).values(
            "astro_object__id", "astro_object__name"
        ).distinct()
        print("This reference has {0} astro_objects".format(astro_objects.count()))

        import numpy
        observations_array = numpy.array(relevant_observations.order_by("id").values_list(
            "astro_object__id", "parameter__id", "value", "sigma_up", "sigma_down"
        ))
        print("This reference has {0} observations".format(len(observations_array)))

        dtype = [("name", "|U16" )] + [(p_name, "|U16") for p_name in parameter_names]
        observations = numpy.empty(astro_objects.count(), dtype=dtype)
        for i, ao in enumerate(astro_objects):
            observations[i]["name"] = ao["astro_object__name"]
            for j, p in enumerate(parameters):
                has_obs, = numpy.where(
                    (observations_array[:,0] == ao["astro_object__id"])
                    & (observations_array[:,1] == p["parameter__id"])
                )
                if len(has_obs) == 1:  # TODO: handle multiple observations of same cluster/parameter
                    observations[i][p["parameter__name"]] = observations_array[has_obs,2][0]

            data[i] = ObservationTable(row={k: v for k,v in zip(["name"] + parameter_names, observations[i])})

        serializer = ObservationTableSerializer(instance=data, many=True)
        return Response({
            "count": len(data),
            "next": None,
            "previous": None,
            "results": serializer.data
        })
