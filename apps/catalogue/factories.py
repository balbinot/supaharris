import logging
import factory
from faker import Factory
from django.conf import settings

from catalogue.models import (
    Parameter,
    Reference,
    AstroObjectClassification,
    AstroObject,
    Profile,
    Auxiliary,
    Observation,
    Rank,
)


faker = Factory.create("en_UK")
logger = logging.getLogger(__name__)


class ParameterFactory(factory.DjangoModelFactory):
    class Meta:
        model = Parameter
        django_get_or_create = ("name",)

    name = factory.LazyAttribute(lambda _: faker.name())
    description = factory.LazyAttribute(lambda _: faker.text(
        max_nb_chars=faker.random_int(min=42, max=255)
    ))
    unit = "unit"
    scale = 1.0


class ReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Reference
        django_get_or_create = ("ads_url",)

    ads_url = factory.LazyAttribute(lambda _: faker.url())
    journal = factory.LazyAttribute(lambda _:
        faker.random_int(min=0, max=len(Reference.JOURNALS))
    )

    @factory.post_generation
    def astro_objects(self, create, extracted, **kwargs):
        # ForeignKey relation at Subcategory. Here we use the related_name
        if not create or kwargs.get("skip"):
            return

        if extracted:
            for astro_object in extracted:
                self.astro_objects.add(astro_object)
            return

        for i in range(faker.random_int(min=0, max=10)):
            # self.astro_objects.add(AstroObject.objects.create()
            break


class AstroObjectClassificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = AstroObjectClassification
        django_get_or_create = ("name",)

    name = factory.LazyAttribute(lambda _: faker.name())
    abbreviation = factory.LazyAttribute(lambda _: faker.name())


class AstroObjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = AstroObject
        django_get_or_create = ("name",)

    name = factory.LazyAttribute(lambda _: faker.name())

    @factory.post_generation
    def classifications(self, create, extracted, **kwargs):
        # ForeignKey relation at Subcategory. Here we use the related_name
        if not create or kwargs.get("skip"):
            return

        if extracted:
            for classification in extracted:
                self.classifications.add(classification)
            return

        for i in range(faker.random_int(min=0, max=10)):
            # self.classifications.add(AstroObjectClassification.objects.create()
            break


class ProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = Profile

    profile_type = factory.LazyAttribute(lambda _: faker.name())
    # reference
    # astro_object
    # profile_type
    # profile
    # model_parameters
    # model_flavour


class AuxiliaryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Auxiliary
        django_get_or_create = ("name",)

    # reference
    # astro_object
    # path
    # url


class ObservationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Observation

    # reference
    # astro_object
    # parameter

    # value
    # sigma_up
    # sigma_down


class RankFactory(factory.DjangoModelFactory):
    class Meta:
        model = Rank

    # observation

    # rank
    # weight
    # compilation_name
