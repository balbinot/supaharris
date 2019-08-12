from rest_framework import viewsets
from rest_framework import filters
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from catalogue.models import (
    Reference,
    AstroObject,
    AstroObjectClassification,
    Parameter,
    Observation,
)
from catalogue.serializers import (
    ReferenceSerializer,
    AstroObjectSerializer,
    AstroObjectClassificationSerializer,
    ParameterSerializer,
    ObservationSerializer,
)


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class AstroObjectClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AstroObjectClassification.objects.all()
    serializer_class = AstroObjectClassificationSerializer


class AstroObjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AstroObject.objects.all()
    serializer_class = AstroObjectSerializer


class ParameterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer


class ObservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("astro_object", "parameter", "reference")
