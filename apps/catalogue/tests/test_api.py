import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
from catalogue.factories import (
    ParameterFactory,
    ReferenceFactory,
    AstroObjectClassificationFactory,
    AstroObjectFactory,
    ProfileFactory,
    AuxiliaryFactory,
    ObservationFactory,
    RankFactory,
)
from tests.test_api import AnonReadOnlyAPITestCase


class ReferenceViewSetTestCase(AnonReadOnlyAPITestCase, APITestCase):
    @classmethod
    def setUpTestData(cls):
        ReferenceFactory.create_batch(2)
        super().setUpTestData()

    def setUp(self):
        # Set the admin + user tokens
        super().setUp()

        # Set the detail for this specific test
        self.list_uri = "reference-list"
        self.detail_uri = "reference-detail"
        self.detail_pk = Reference.objects.last().pk
        self.count = Reference.objects.count()
        self.data_orm = Reference.objects.order_by("id").first()
        self.data_orm_detail = Reference.objects.get(pk=self.detail_pk)  # last()
        self.serializer_fields = []
        self.resource_name_list = "Reference List"
        self.resource_name_detail = "Reference Instance"


class AstroObjectClassificationViewSetTestCase(AnonReadOnlyAPITestCase, APITestCase):
    fixtures = [
        "fixtures/catalogue_AstroObjectClassification.json",
    ]

    def setUp(self):
        # Set the admin + user tokens
        super().setUp()

        # Set the detail for this specific test
        self.list_uri = "astroobjectclassification-list"
        self.detail_uri = "astroobjectclassification-detail"
        self.detail_pk = AstroObjectClassification.objects.last().pk
        self.count = AstroObjectClassification.objects.count()
        self.data_orm = AstroObjectClassification.objects.order_by("id").first()
        self.data_orm_detail = AstroObjectClassification.objects.get(pk=self.detail_pk)  # last()
        self.serializer_fields = []
        self.resource_name_list = "Astro Object Classification List"
        self.resource_name_detail = "Astro Object Classification Instance"


class AstroObjectViewSetTestCase(AnonReadOnlyAPITestCase, APITestCase):
    @classmethod
    def setUpTestData(cls):
        AstroObjectFactory.create_batch(2)
        super().setUpTestData()

    def setUp(self):
        # Set the admin + user tokens
        super().setUp()

        # Set the detail for this specific test
        self.list_uri = "astroobject-list"
        self.detail_uri = "astroobject-detail"
        self.detail_pk = AstroObject.objects.last().pk
        self.count = AstroObject.objects.count()
        self.data_orm = AstroObject.objects.order_by("id").first()
        self.data_orm_detail = AstroObject.objects.get(pk=self.detail_pk)  # last()
        self.serializer_fields = []
        self.resource_name_list = "Astro Object List"
        self.resource_name_detail = "Astro Object Instance"


class ParameterViewSetTestCase(AnonReadOnlyAPITestCase, APITestCase):
    fixtures = [
        "fixtures/catalogue_Parameter.json",
    ]

    def setUp(self):
        # Set the admin + user tokens
        super().setUp()

        # Set the detail for this specific test
        self.list_uri = "parameter-list"
        self.detail_uri = "parameter-detail"
        self.detail_pk = Parameter.objects.last().pk
        self.count = Parameter.objects.count()
        self.data_orm = Parameter.objects.order_by("id").first()
        self.data_orm_detail = Parameter.objects.get(pk=self.detail_pk)  # last()
        self.serializer_fields = []
        self.resource_name_list = "Parameter List"
        self.resource_name_detail = "Parameter Instance"


class ObservationViewSetTestCase(AnonReadOnlyAPITestCase, APITestCase):
    @classmethod
    def setUpTestData(cls):
        ObservationFactory.create_batch(151)
        super().setUpTestData()

    def setUp(self):
        # Set the admin + user tokens
        super().setUp()

        # Set the detail for this specific test
        self.list_uri = "observation-list"
        self.detail_uri = "observation-detail"
        self.detail_pk = Observation.objects.last().pk
        self.count = Observation.objects.count()
        self.data_orm = Observation.objects.order_by("id").first()
        self.data_orm_detail = Observation.objects.get(pk=self.detail_pk)  # last()
        self.serializer_fields = []
        self.resource_name_list = "Observation List"
        self.resource_name_detail = "Observation Instance"

    def test_json_paginator(self):
        for page_size in [1, 10, 50, 100, 150]:
            uri = reverse(self.list_uri) + "?format=json&length={0}".format(page_size)
            response = self.client.get(uri)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertEqual(len(data["results"]), page_size)

    def test_datatables_paginator(self):
        for page_size in [1, 10, 50, 100, 150]:
            uri = reverse(self.list_uri) + "?format=datatables&length={0}".format(page_size)
            response = self.client.get(uri)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["data"]), page_size)
