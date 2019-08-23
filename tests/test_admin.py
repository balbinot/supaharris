from django.urls import reverse

from accounts.factories import (
    UserModelFactory,
    AdminFactory,
)


class AdminTestCase(object):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.admin = AdminFactory()
        self.admin_password = "admin_password"
        self.admin.set_password(self.admin_password)
        self.admin.save()

        self.user = UserModelFactory()
        self.user_password = "user_password"
        self.user.set_password(self.user_password)
        self.user.save()

        self.admin_changelist_uri = "admin:{0}_changelist".format(self.admin_url_name)
        self.admin_add_uri = "admin:{0}_add".format(self.admin_url_name)
        self.admin_change_uri = "admin:{0}_change".format(self.admin_url_name)
        self.admin_delete_uri = "admin:{0}_delete".format(self.admin_url_name)
        self.admin_history_uri = "admin:{0}_history".format(self.admin_url_name)

    def tearDown(self, *args, **kwargs):
        self.admin.delete()
        self.user.delete()
        super().tearDown(*args, **kwargs)

    def test_login_of_admin_200(self):
        response = self.client.get(reverse("admin:login"))
        self.assertTemplateUsed(response, "admin/login.html")
        self.assertEqual(response.status_code, 200)
        login_status = self.client.login(email=self.admin.email, password=self.admin_password)
        self.assertTrue(login_status)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)

    def test_login_of_user_302(self):
        response = self.client.get(reverse("admin:login"))
        self.assertTemplateUsed(response, "admin/login.html")
        self.assertEqual(response.status_code, 200)  # login form is fine
        login_status = self.client.login(email=self.user.email, password=self.user_password)
        self.assertTrue(login_status)  # b/c admin login forms works for any user

        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)  # the index is not fine
        self.assertEqual(response.url, "/admin/login/?next=/admin/")

    def test_get_admin_changelist_is_superuser_200(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        response = self.client.get(reverse(self.admin_changelist_uri))
        self.assertEqual(response.status_code, 200)

    def test_get_admin_changelist_is_authenticated_302(self):
        self.client.login(email=self.user.email, password=self.user_password)
        uri = reverse(self.admin_changelist_uri)
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/login/?next="+uri)

    def test_get_admin_add_is_superuser_200(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        uri = reverse(self.admin_add_uri)
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)

    def test_post_admin_add_is_superuser_200(self):
        pass

    def test_get_admin_add_is_authenticated_302(self):
        self.client.login(email=self.user.email, password=self.user_password)
        uri = reverse(self.admin_add_uri)
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/login/?next="+uri)

    def test_get_admin_change_is_superuser_200(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        uri = reverse(self.admin_change_uri, args=[self.admin_instance_pk])
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)

    def test_get_admin_change_is_authenticated_302(self):
        self.client.login(email=self.user.email, password=self.user_password)
        uri = reverse(self.admin_change_uri, args=[self.admin_instance_pk])
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/login/?next="+uri)

    def test_get_admin_delete_is_superuser_200(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        uri = reverse(self.admin_delete_uri, args=[self.admin_instance_pk])
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)

    def test_post_admin_delete_is_superuser_200(self):
        pass

    def test_get_admin_delete_is_authenticated_302(self):
        self.client.login(email=self.user.email, password=self.user_password)
        uri = reverse(self.admin_delete_uri, args=[self.admin_instance_pk])
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/login/?next="+uri)

    def test_get_admin_history_is_superuser_200(self):
        self.client.login(email=self.admin.email, password=self.admin_password)
        uri = reverse(self.admin_history_uri, args=[self.admin_instance_pk])
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)

    def test_get_admin_history_is_authenticated_302(self):
        self.client.login(email=self.user.email, password=self.user_password)
        uri = reverse(self.admin_history_uri, args=[self.admin_instance_pk])
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/login/?next="+uri)

    def test_admin_detail_view_can_be_saved(self):
        pass

    def test_admin_save_updates_last_updated_by(self):
        pass

    def test_get_count(self):
        pass
