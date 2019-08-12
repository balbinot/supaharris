from rest_framework import serializers

from catalogue.models import (
    Reference,
    AstroObject,
    AstroObjectClassification,
    Parameter,
    Observation,
)


class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    frontend_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reference
        fields = (
            "id", "slug", "ads_url", "first_author", "authors", "title",
            "journal", "doi", "year", "month", "volume", "pages", "url", "frontend_url",
        )
        datatables_always_serialize = ("id",)

    def get_frontend_url(self, obj):
        return self.context["request"].scheme + "://" + self.context["request"].get_host() + obj.get_absolute_url()


class ObservationSerializerForAstroObject(serializers.ModelSerializer):
    parameter = serializers.CharField(source="parameter.name")

    class Meta:
        model = Observation
        fields = ("parameter", "value", "sigma_up", "sigma_down")


class AstroObjectClassificationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = AstroObjectClassification
        fields = (
            "id", "name", "slug",
        )
        datatables_always_serialize = ("id",)


class AstroObjectSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    frontend_url = serializers.SerializerMethodField(read_only=True)
    observations = ObservationSerializerForAstroObject(source="observation_set", many=True)
    classifications = serializers.StringRelatedField(many=True)

    class Meta:
        model = AstroObject
        fields = (
            "id", "name", "slug", "altname", "url", "frontend_url",
            "observations", "classifications",
        )
        datatables_always_serialize = ("id",)

    def get_frontend_url(self, obj):
        return self.context["request"].scheme + "://" + self.context["request"].get_host() + obj.get_absolute_url()




class ParameterSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    frontend_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Parameter
        fields = (
            "id", "name", "slug", "description", "unit", "scale", "url", "frontend_url",
        )
        datatables_always_serialize = ("id",)

    def get_frontend_url(self, obj):
        return self.context["request"].scheme + "://" + self.context["request"].get_host() + obj.get_absolute_url()


class ObservationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Observation
        fields = (
            "astro_object", "id", "parameter", "value", "sigma_up", "sigma_down", "reference", "url",
        )
        datatables_always_serialize = ("id",)
        depth = 1
