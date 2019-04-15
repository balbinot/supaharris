from django.views import generic
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

from accounts.models import UserModel
from accounts.forms import UserModelCreationForm


class RegisterView(generic.CreateView):
    form_class = UserModelCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        valid = super(RegisterView, self).form_valid(form)
        email, password = form.cleaned_data.get('email'), form.cleaned_data.get('password1')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
            return valid
        # No else on purpose. We'll see what breaks so we can fix it :-) ..


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
