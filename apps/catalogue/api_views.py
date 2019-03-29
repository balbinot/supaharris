from rest_framework import viewsets

from catalogue.models import GlobularCluster
from catalogue.serializers import GlobularClusterSerializer


class GlobularClusterViewSet(viewsets.ModelViewSet):
    queryset = GlobularCluster.objects.all()
    serializer_class = GlobularClusterSerializer
