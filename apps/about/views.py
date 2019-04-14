from django.utils import timezone
from django.shortcuts import render

from about.models import PrivacyPolicy


def info(request):
    return render(request, "about/info.html", {})


def privacy_policy(request):
    policy = PrivacyPolicy.objects.first()

    if not policy:
        class PrivacyPolicyDefault(object):
            def __init__(self):
                self.date = timezone.now()
                self.content = "We are slacking - we have not implemented the boring legal boilerplate"
        policy = PrivacyPolicyDefault()
    return render(request, "about/privacy_policy.html", {"policy": policy})


def handler404(request):
    return render(request, "404.html")

def handler500(request):
    return render(request, "500.html")
