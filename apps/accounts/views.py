from accounts.forms import UserModelCreationForm
from accounts.models import UserModel
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic


class RegisterView(generic.CreateView):
    form_class = UserModelCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        valid = super(RegisterView, self).form_valid(form)
        email, password = (
            form.cleaned_data.get("email"),
            form.cleaned_data.get("password1"),
        )
        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
            return valid
        # No else on purpose. We'll see what breaks so we can fix it :-) ..


class PasswordResetView(auth_views.PasswordResetView):
    def form_valid(self, form):
        valid = super().form_valid(form)
        # TODO: Passing email via extra_context to auth_views.PasswordResetView
        # in accounts.urls breaks, so we drop the email in the session storage ..
        # but we'd like to avoid that...
        email = form.cleaned_data.get("email")
        self.request.session["password_reset_email"] = email
        return valid


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
