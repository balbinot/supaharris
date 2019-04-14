from rest_framework import serializers

from catalogue.models import Reference
from catalogue.models import GlobularCluster


class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reference
        fields = ("id", "bib_code", "ads_url" )
        datatables_always_serialize = ("id",)


class GlobularClusterSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = GlobularCluster
        fields = ("id", "name", "slug", "altname",)
        datatables_always_serialize = ("id",)
