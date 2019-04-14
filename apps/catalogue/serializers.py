from rest_framework import serializers

from catalogue.models import GlobularCluster


class GlobularClusterSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = GlobularCluster
        fields = ("id", "name", "slug", "altname",)
        datatables_always_serialize = ("id",)
