from rest_framework import viewsets
from rest_framework import filters
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from catalogue.models import Reference
from catalogue.models import GlobularCluster
from catalogue.models import Parameter
from catalogue.models import Observation
from catalogue.serializers import ReferenceSerializer
from catalogue.serializers import GlobularClusterSerializer
from catalogue.serializers import ParameterSerializer
from catalogue.serializers import ObservationSerializer


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class GlobularClusterViewSet(viewsets.ModelViewSet):
    queryset = GlobularCluster.objects.all()
    serializer_class = GlobularClusterSerializer


class ParameterViewSet(viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("cluster", "parameter", "reference")
