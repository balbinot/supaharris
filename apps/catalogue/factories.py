import numpy
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


def generate_bib_code(author=None, year=None, journal=None, volume=None, pages=None):
    if not author:
        author = faker.last_name()
    if not year:
        year = faker.year()
    if not journal:
        journals = [k.upper()[0:8] for k,v in Reference.JOURNALS]
        journal = journals[faker.random_int(min=0, max=len(journals))]
    if not volume:
        volume = faker.random_int(min=1, max=450)
    if not pages:
        pages = faker.random_int(min=1, max=5000)
    bib_code = "{0}{1:.<6}{2:.>3}{3:.>4}{4}".format(
        year,
        journal,
        volume,
        pages,
        author.upper()[0]
    )
    return bib_code


class ReferenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Reference

    title = factory.LazyAttribute(lambda _: faker.sentence())
    first_author = factory.LazyAttribute(lambda _: faker.last_name())
    journal = factory.LazyAttribute(lambda _:
        faker.random_int(min=0, max=len(Reference.JOURNALS)-1)
    )
    year = factory.LazyAttribute(lambda _: faker.year())
    month = factory.LazyAttribute(lambda _: faker.random_int(min=1, max=12))
    volume = factory.LazyAttribute(lambda _: faker.random_int(min=1, max=450))
    pages = factory.LazyAttribute(lambda _: faker.random_int(min=1, max=450))
    bib_code = factory.LazyAttribute(lambda _:
        generate_bib_code(
            _.first_author,
            _.year,
            Reference.JOURNALS[_.journal][0].upper()[0:8],
            _.volume,
            _.pages,
        )
    )
    ads_url = factory.LazyAttribute(lambda _:
        "https://example.com/fake/{0}".format(_.bib_code)
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

    reference = factory.SubFactory(ReferenceFactory)
    astro_object = factory.SubFactory(AstroObjectFactory)

    x = list(range(0, 10, 1))
    y = factory.LazyAttribute(lambda _: [i**2 for i in _.x])
    x_description = factory.Sequence(lambda n: "x{0}".format(n))
    y_description = factory.Sequence(lambda n: "y{0}".format(n))


class AuxiliaryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Auxiliary

    reference = factory.SubFactory(ReferenceFactory)
    astro_object = factory.SubFactory(AstroObjectFactory)
    # path
    # url


class ObservationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Observation

    reference = factory.SubFactory(ReferenceFactory)
    astro_object = factory.SubFactory(AstroObjectFactory)
    parameter = factory.SubFactory(ParameterFactory)

    value = factory.LazyAttribute(lambda _:
        faker.random_int(min=-999999, max=999999) / 1000
    )
    # sigma_up
    # sigma_down


class RankFactory(factory.DjangoModelFactory):
    class Meta:
        model = Rank

    observation = factory.SubFactory(ObservationFactory)
    rank = factory.LazyAttribute(lambda _: faker.random_int(min=0, max=20))
    weight = factory.LazyAttribute(lambda _: faker.random_int(min=0, max=20))
    # compilation_name
