from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

from accounts import views
from accounts.forms import SetPasswordForm
from accounts.forms import PasswordResetForm
from accounts.forms import PasswordChangeForm
from accounts.views import PasswordChangeDoneView


app_name = "accounts"
urlpatterns = [
    path("create/", views.create_account, name="create"),
    path("email-sent/", views.activation_sent, name="activation_sent"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("login/", views.user_login, name="user_login"),
    path("profile/", views.profile, name="profile"),
    path("delete/", views.delete_account, name="delete_account"),

    # Adapted from Django"s built-in class-based auth views
    path("logout/", auth_views.LogoutView.as_view(
        template_name=reverse_lazy("index")), name="logout"),

    path("password_change/", auth_views.PasswordChangeView.as_view(
        form_class=PasswordChangeForm,
        template_name="accounts/password_change_form.html",
        success_url=reverse_lazy("accounts:password_change_done")),
        name="password_change"),
    path("password_change/done/", PasswordChangeDoneView.as_view(
        template_name="accounts/profile.html"),
        name="password_change_done"),

    path("password-reset", auth_views.PasswordResetView.as_view(
        form_class=PasswordResetForm,
        success_url=reverse_lazy("accounts:password_reset_done"),
        template_name="accounts/password_reset_form.html",
        email_template_name="accounts/password_reset_email.html"),
        name="password_reset"),
    path("password-reset/mail-sent/", auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"),
        name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        form_class=SetPasswordForm,
        template_name="accounts/password_reset_confirm.html",
        success_url=reverse_lazy("accounts:password_reset_complete")),
        name="password_reset_confirm"),
    path("password-reset/done/", views.password_reset_complete,
        name="password_reset_complete"),
]
