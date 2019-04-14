from rest_framework import viewsets

from catalogue.models import Reference
from catalogue.models import GlobularCluster
from catalogue.serializers import ReferenceSerializer
from catalogue.serializers import GlobularClusterSerializer


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class GlobularClusterViewSet(viewsets.ModelViewSet):
    queryset = GlobularCluster.objects.all()
    serializer_class = GlobularClusterSerializer
