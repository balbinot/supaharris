from catalogue.factories import (
    AstroObjectClassificationFactory,
    AstroObjectFactory,
    AuxiliaryFactory,
    ObservationFactory,
    ParameterFactory,
    ProfileFactory,
    RankFactory,
    ReferenceFactory,
)
from catalogue.models import (
    AstroObject,
    AstroObjectClassification,
    Auxiliary,
    Observation,
    Parameter,
    Profile,
    Rank,
    Reference,
)
from django.contrib.sites.models import Site
from django.test import TestCase
from tests.test_admin import AdminTestCase


class ParameterAdminTestCase(AdminTestCase, TestCase):
    fixtures = [
        "fixtures/catalogue_Parameter.json",
    ]

    def setUp(self):
        self.admin_url_name = "catalogue_parameter"
        self.admin_instance_pk = Parameter.objects.last().pk
        self.count = Parameter.objects.count()

        super().setUp()


class ReferenceAdminTestCase(AdminTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        ReferenceFactory.create_batch(2)
        super().setUpTestData()

    def setUp(self):
        self.admin_url_name = "catalogue_reference"
        self.admin_instance_pk = Reference.objects.last().pk
        self.count = Reference.objects.count()

        super().setUp()


class AstroObjectClassificationAdminTestCase(AdminTestCase, TestCase):
    fixtures = [
        "fixtures/catalogue_AstroObjectClassification.json",
    ]

    def setUp(self):
        self.admin_url_name = "catalogue_astroobjectclassification"
        self.admin_instance_pk = AstroObjectClassification.objects.last().pk
        self.count = AstroObjectClassification.objects.count()

        super().setUp()


class AstroObjectAdminTestCase(AdminTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        AstroObjectFactory.create_batch(2)
        super().setUpTestData()

    def setUp(self):
        self.admin_url_name = "catalogue_astroobject"
        self.admin_instance_pk = AstroObject.objects.last().pk
        self.count = AstroObject.objects.count()

        super().setUp()


class ProfileAdminTestCase(AdminTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        ProfileFactory.create_batch(2)
        super().setUpTestData()

    def setUp(self):
        self.admin_url_name = "catalogue_profile"
        self.admin_instance_pk = Profile.objects.last().pk
        self.count = Profile.objects.count()

        super().setUp()


class AuxiliaryAdminTestCase(AdminTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        AuxiliaryFactory.create_batch(2)
        super().setUpTestData()

    def setUp(self):
        self.admin_url_name = "catalogue_auxiliary"
        self.admin_instance_pk = Auxiliary.objects.last().pk
        self.count = Auxiliary.objects.count()

        super().setUp()


class ObservationAdminTestCase(AdminTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        ObservationFactory.create_batch(2)
        super().setUpTestData()

    def setUp(self):
        self.admin_url_name = "catalogue_observation"
        self.admin_instance_pk = Observation.objects.last().pk
        self.count = Observation.objects.count()

        super().setUp()


class RankAdminTestCase(AdminTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        RankFactory.create_batch(2)
        super().setUpTestData()

    def setUp(self):
        self.admin_url_name = "catalogue_rank"
        self.admin_instance_pk = Rank.objects.last().pk
        self.count = Rank.objects.count()

        super().setUp()
