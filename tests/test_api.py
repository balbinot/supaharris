from accounts.factories import AdminFactory, UserModelFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APILiveServerTestCase,
    APIRequestFactory,
    APISimpleTestCase,
    APITestCase,
    APITransactionTestCase,
)


class AnonReadOnlyAPITestCase(object):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)  # in case of inheritance

        self.admin = AdminFactory()
        self.admin_password = "admin_password"
        self.admin.set_password(self.admin_password)
        self.admin.save()

        self.user = UserModelFactory()
        self.user_password = "user_password"
        self.user.set_password(self.user_password)
        self.user.save()

    def tearDown(self, *args, **kwargs):
        self.admin.delete()
        self.user.delete()
        super().tearDown(*args, **kwargs)

    def test_login_of_admin_200(self):
        login_status = self.client.login(
            email=self.admin.email, password=self.admin_password
        )
        self.assertTrue(login_status)
        response = self.client.get(reverse("api-root"))
        self.assertEqual(response.status_code, 200)

    def test_login_of_user_200(self):
        login_status = self.client.login(
            email=self.user.email, password=self.user_password
        )
        self.assertTrue(login_status)
        response = self.client.get(reverse("api-root"))
        self.assertEqual(response.status_code, 200)

    ### HEAD requests --> allowed for anon, user and admin
    def test_head_list_user_is_anonymous_200(self):
        response = self.client.head(reverse(self.list_uri))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Allow"], "GET, HEAD, OPTIONS")
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response["Vary"], "Accept, Accept-Language, Cookie")

        response = self.client.head(reverse(self.detail_uri, args=[self.detail_pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Allow"], "GET, HEAD, OPTIONS")
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response["Vary"], "Accept, Accept-Language, Cookie")

    def test_head_user_is_authenticated_200(self):
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.head(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.head(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_head_user_is_superuser_200(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        response = self.client.head(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.head(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    ### OPTIONS requests --> allowed for anon, user and admin
    def verify_options_data(self, response):
        self.assertIn("name", response.data.keys())
        self.assertIsInstance(response.data["name"], str)
        self.assertIn("description", response.data.keys())
        self.assertIsInstance(response.data["description"], str)
        self.assertIn("renders", response.data.keys())
        self.assertIn("application/json", response.data["renders"])
        self.assertIn("text/html", response.data["renders"])
        self.assertIsInstance(response.data["renders"], list)
        self.assertIn("parses", response.data.keys())
        self.assertIsInstance(response.data["parses"], list)
        self.assertIn("application/json", response.data["parses"])
        self.assertIn("application/x-www-form-urlencoded", response.data["parses"])
        self.assertIn("multipart/form-data", response.data["parses"])

    def test_options_user_is_anonymous_200(self):
        response = self.client.options(reverse(self.list_uri))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verify_options_data(response)
        self.assertEqual(response.data["name"], self.resource_name_list)  # Sanity check

        response = self.client.options(reverse(self.detail_uri, args=[self.detail_pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["name"], self.resource_name_detail
        )  # Sanity check
        self.verify_options_data(response)

    def test_options_user_is_authenticated_200(self):
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.options(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.options(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_options_user_is_superuser_200(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        response = self.client.options(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.options(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    ### GET requests --> allowed for anon, user and admin
    def verify_get_response_data_results(self, data_api, data_orm):
        """ Verify that the 'actual' data in the list/detail response is correct """
        # self.assertEqual(len(data_api.keys()), len(self.serializer_fields))
        # self.assertEqual(list(data_api.keys()), self.serializer_fields)
        for field in self.serializer_fields:
            # TODO: handle FK and M2M
            print(
                "\n{0}\napi -> {1}: {2}\norm -> {3}: {4}".format(
                    field,
                    data_api[field],
                    type(data_api[field]),
                    getattr(data_orm, field),
                    type(getattr(data_orm, field)),
                )
            )
            self.assertEqual(data_api[field], getattr(data_orm, field))

    def verify_get_list_response_data(self, response):
        self.assertIn("count", response.data.keys())
        self.assertIn("next", response.data.keys())
        self.assertIn("previous", response.data.keys())
        self.assertIn("results", response.data.keys())

        self.assertEqual(response.data["count"], self.count)
        data_api = response.data["results"][0]
        self.verify_get_response_data_results(data_api, self.data_orm)

    def verify_get_detail_response_data(self, response):
        data_api = response.data
        self.verify_get_response_data_results(data_api, self.data_orm_detail)

    def test_get_user_is_anonymous_200(self):
        response = self.client.get(reverse(self.list_uri))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verify_get_list_response_data(response)

        response = self.client.get(reverse(self.detail_uri, args=[self.detail_pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verify_get_detail_response_data(response)

    def test_get_user_is_authenticated_200(self):
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.get(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verify_get_list_response_data(response)

        response = self.client.get(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verify_get_detail_response_data(response)

    def test_get_user_is_superuser_200(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        response = self.client.get(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verify_get_list_response_data(response)

        response = self.client.get(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.verify_get_detail_response_data(response)

    ### POST requests --> disabled for anon, user and admin
    def test_post_user_is_anonymous_403(self):
        response = self.client.post(reverse(self.list_uri))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(reverse(self.detail_uri, args=[self.detail_pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_user_is_authenticated_403(self):
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.post(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_user_is_superuser(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        response = self.client.post(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ### PUT requests --> disabled for anon, user and admin
    def test_put_user_is_anonymous_403(self):
        response = self.client.put(reverse(self.list_uri))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(reverse(self.detail_uri, args=[self.detail_pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_user_is_authenticated_403(self):
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.put(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_user_is_superuser_405(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        response = self.client.put(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ### PATCH requests --> disabled for anon, user and admin
    def test_patch_user_is_anonymous_403(self):
        response = self.client.patch(reverse(self.list_uri))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(reverse(self.detail_uri, args=[self.detail_pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_is_authenticated_403(self):
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.patch(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_is_superuser_405(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        response = self.client.patch(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ### DELETE requests --> disabled for anon, user and admin
    def test_delete_user_is_anonymous_403(self):
        response = self.client.delete(reverse(self.list_uri))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(reverse(self.detail_uri, args=[self.detail_pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_is_authenticated_403(self):
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.delete(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_is_superuser_405(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        response = self.client.delete(reverse(self.list_uri),)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(reverse(self.detail_uri, args=[self.detail_pk]),)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
