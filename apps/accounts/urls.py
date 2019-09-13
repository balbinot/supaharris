from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

from accounts.views import profile
from accounts.views import RegisterView
from accounts.views import PasswordResetView

app_name = "accounts"  # namespace the urls
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    # TODO wrapper around LoginView w/ remember_me cookie
    path("login/", auth_views.LoginView.as_view(
        template_name="accounts/login.html"), name="login"),
    path("profile/", profile, name="profile"),
    path("logout/", auth_views.LogoutView.as_view(
        template_name="accounts/logged_out.html"), name="logout"),

    path("password_change/", auth_views.PasswordChangeView.as_view(
        template_name="accounts/password_change_form.html",
        success_url=reverse_lazy("accounts:password_change_done"),
        ), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="accounts/password_change_done.html"), name="password_change_done"),

    path("password_reset/", PasswordResetView.as_view(
        template_name="accounts/password_reset_form.html",
        email_template_name="accounts/password_reset_email.html",
        subject_template_name="accounts/password_reset_subject.txt",
        success_url=reverse_lazy("accounts:password_reset_done")),
        name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url=reverse_lazy("accounts:password_reset_complete"),
        ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
]
