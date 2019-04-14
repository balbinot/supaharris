from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views

from accounts.views import profile
from accounts.views import RegisterView

app_name = "accounts"  # namespace the urls
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(
        template_name='accounts/login.html'), name='login'),
    path('profile/', profile, name='profile'),
    path('logout/', views.LogoutView.as_view(
        template_name='accounts/logged_out.html'), name='logout'),

    path('password_change/', views.PasswordChangeView.as_view(
        template_name='accounts/password_change_form.html' ), name='password_change'),
    path('password_change/done/', views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), name='password_change_done'),

    path('password_reset/', views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done'),
        extra_context={"hank": "moody"}
        ),
        name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete'),
        ), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
