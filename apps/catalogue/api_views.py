from rest_framework import viewsets
from rest_framework import filters
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from catalogue.models import Reference
from catalogue.models import AstroObject
from catalogue.models import Parameter
from catalogue.models import Observation
from catalogue.serializers import ReferenceSerializer
from catalogue.serializers import AstroObjectSerializer
from catalogue.serializers import ParameterSerializer
from catalogue.serializers import ObservationSerializer


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


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
    filterset_fields = ("cluster", "parameter", "reference")
