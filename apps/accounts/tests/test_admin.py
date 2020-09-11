from accounts.factories import UserModelFactory
from accounts.models import UserModel
from django.contrib.sites.models import Site
from django.test import TestCase
from tests.test_admin import AdminTestCase


class ParameterAdminTestCase(AdminTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        UserModelFactory.create_batch(10 - UserModel.objects.count())
        super().setUpTestData()

    def setUp(self):
        # Set the detail for this specific test
        self.admin_url_name = "accounts_usermodel"
        self.admin_instance_pk = UserModel.objects.last().pk
        self.count = UserModel.objects.count()

        super().setUp()
