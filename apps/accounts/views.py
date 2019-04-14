from django.views import generic
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from accounts.forms import UserModelCreationForm


class RegisterView(generic.CreateView):
    form_class = UserModelCreationForm
    success_url = reverse_lazy('accounts:profile')
    template_name = 'accounts/register.html'


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
