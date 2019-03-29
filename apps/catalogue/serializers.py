from rest_framework import serializers

from catalogue.models import GlobularCluster


class GlobularClusterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GlobularCluster
        fields = ("name",)
