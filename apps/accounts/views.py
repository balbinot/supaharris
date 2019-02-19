from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry

from accounts.models import UserModel
from accounts.forms import SignUpForm
from accounts.forms import ProfileForm
from accounts.forms import DeleteAccountForm


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(data=request.POST, instance=get_object_or_404(UserModel, pk=request.user.pk))
        if form.is_valid():
            user = form.save()

            # Add record to LogEntry
            content_type_pk = ContentType.objects.get_for_model(UserModel).pk
            LogEntry.objects.log_action(
                user.pk, content_type_pk, user.pk, str(user), CHANGE,
                change_message="User updated profile via website."
            )

            return render(request, "accounts/profile.html", {"profile_form": form})
    else:
        form = ProfileForm(instance=get_object_or_404(UserModel, pk=request.user.pk))

    return render(request, "accounts/profile.html", {"profile_form": form})

@login_required
def delete_account(request):
    form = DeleteAccountForm(data=request.POST)
    user = get_object_or_404(UserModel, pk=request.user.pk)
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["email"]
            if email == request.user.email:
                logout(request)  # logout expects requests, not user
                user.delete()
                messages.info(request, "Account deleted.")
            else:
                messages.info(request, "Error: email addresses did not match!")
        else:
            messages.error(request, "Error: email addresses is invalid!")

    return render(request, "accounts/delete.html", {"delete_form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)

                # If remember me, remember session for 2 weeks
                if request.POST.get("remember-me", False):
                    request.session.set_expiry(1209600)

                return redirect("accounts:profile")
        else:
            error_msg = "<p> Invalid username or password </p>"
            content = {"content": error_msg}

    return render(request, "accounts/login.html", {})

def create_account(request):
    if request.method == "POST":
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)

            msg_params = {
                "user": user,
                "protocol": request.scheme,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                "token": default_token_generator.make_token(user),
            }

            msg_plain = render_to_string("accounts/welcome_email.txt", msg_params)
            msg_html = render_to_string("accounts/welcome_email.html", msg_params)
            subject="SupaHarris: please confirm email address"
            from_email=settings.DEFAULT_FROM_EMAIL
            recipients=[user.email]

            msg = EmailMultiAlternatives(subject, msg_plain, from_email, recipients)
            msg.attach_alternative(msg_html, "text/html")
            msg.send()

            # Add record to LogEntry
            content_type_pk = ContentType.objects.get_for_model(UserModel).pk
            LogEntry.objects.log_action(
                user.pk, content_type_pk, user.pk, str(user), CHANGE,
                change_message="User signed up."
            )

            return redirect("accounts:activation_sent")
    else:
        form = SignUpForm()

    return render(request, "accounts/create_account.html", {"form": form})


def activation_sent(request):
    return render(request, "accounts/activation_sent.html", {})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        login(request, user)
        messages.success(request, "Your account has been succesfully activated!")
        user.save()

        # Add record to LogEntry
        content_type_pk = ContentType.objects.get_for_model(UserModel).pk
        LogEntry.objects.log_action(
            user.pk, content_type_pk, user.pk, str(user), CHANGE,
            change_message="Email address confirmed by user."
        )

        return render(request, "accounts/profile.html")

    return render(request, "accounts/activation_failed.html")


def password_reset_complete(request):
    messages.success(request, "Your password has succesfully been reset.")
    return render(request, "accounts/profile.html")


class PasswordChangeDoneView(PasswordChangeDoneView):
    def get_context_data(self, **kwargs):
        messages.success(self.request, "Your password has succesfully been updated.")
        context = super().get_context_data(**kwargs)
        return context
