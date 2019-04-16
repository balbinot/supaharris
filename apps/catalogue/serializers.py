from rest_framework import serializers

from catalogue.models import Reference
from catalogue.models import GlobularCluster


class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reference
        fields = (
            "id", "slug", "ads_url", "first_author", "authors", "title",
            "journal", "doi", "year", "month", "volume", "pages"
        )
        datatables_always_serialize = ("id",)


class GlobularClusterSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = GlobularCluster
        fields = ("id", "name", "slug", "altname",)
        datatables_always_serialize = ("id",)
