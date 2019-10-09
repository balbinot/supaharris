from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    HyperlinkedModelSerializer,
    ListField,
    CharField,
    IntegerField,
    RelatedField,
    ManyRelatedField,
    StringRelatedField,
    SerializerMethodField,
)

from catalogue.models import (
    Reference,
    AstroObject,
    AstroObjectClassification,
    Parameter,
    Observation,
)


class FrontendUrlMixin(Serializer):
    frontend_url = SerializerMethodField(read_only=True)

    def get_frontend_url(self, obj):
        return self.context["request"].scheme + "://" + self.context["request"].get_host() + obj.get_absolute_url()


class ReferenceListSerializer(FrontendUrlMixin, HyperlinkedModelSerializer):
    id = IntegerField(read_only=True)

    class Meta:
        model = Reference
        fields = (
            "id", "first_author", "year", "title", "url", "ads_url", "frontend_url",
        )
        datatables_always_serialize = ("id",)


class ReferenceDetailSerializer(FrontendUrlMixin, HyperlinkedModelSerializer):
    id = IntegerField(read_only=True)

    class Meta:
        model = Reference
        fields = (
            "id", "slug", "ads_url", "first_author", "authors", "title",
            "journal", "doi", "year", "month", "volume", "pages", "frontend_url",
        )
        datatables_always_serialize = ("id",)


class ObservationSerializerForAstroObjectDetail(ModelSerializer):
    parameter = CharField(source="parameter.name")

    class Meta:
        model = Observation
        fields = ("parameter", "value", "sigma_up", "sigma_down")


class AstroObjectClassificationSerializer(ModelSerializer):
    id = IntegerField(read_only=True)

    class Meta:
        model = AstroObjectClassification
        fields = (
            "id", "name", "slug",
        )
        datatables_always_serialize = ("id",)


class AstroObjectListSerializer(FrontendUrlMixin, HyperlinkedModelSerializer):
    id = IntegerField(read_only=True)
    classifications = StringRelatedField(many=True, read_only=True)

    class Meta:
        model = AstroObject
        fields = (
            "id", "name", "altname", "classifications", "frontend_url",
        )
        datatables_always_serialize = ("id",)


class AstroObjectDetailSerializer(FrontendUrlMixin, HyperlinkedModelSerializer):
    id = IntegerField(read_only=True)
    observations = ObservationSerializerForAstroObjectDetail(many=True)
    classifications = StringRelatedField(many=True, read_only=True)

    class Meta:
        model = AstroObject
        fields = (
            "id", "name", "slug", "altname", "frontend_url",
            "observations", "classifications",
        )
        datatables_always_serialize = ("id",)


class ParameterSerializer(FrontendUrlMixin, HyperlinkedModelSerializer):
    id = IntegerField(read_only=True)

    class Meta:
        model = Parameter
        fields = (
            "id", "name", "slug", "description", "unit", "scale", "frontend_url",
        )
        datatables_always_serialize = ("id",)


class ObservationSerializer(ModelSerializer):
    id = IntegerField(read_only=True)

    class Meta:
        model = Observation
        fields = (
            "id", "astro_object", "parameter", "value", "sigma_up", "sigma_down", "reference",
        )
        datatables_always_serialize = ("id",)
        depth = 1


class ObservationTableSerializer(Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: only use the Parameter instances for which the given Reference has
        # Observation instances ...
        self.fields = {"name": CharField()}
        for p in Parameter.objects.order_by("id"):
            self.fields[p.name] = CharField()
        print(self.fields)

    def to_representation(self, obj):
        return { k: getattr(self.instance[obj], k, None) for k in self.fields }
