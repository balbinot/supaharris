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


def handler404(request, exception=None, template_name=None):
    from sentry_sdk import capture_message
    # capture_message("Page not found!", level="error")

    return render(request, '404.html', { 'request_path': request.path,
        'exception': exception.__class__.__name__ } )


def handler500(request, *args, **argv):
    from sentry_sdk import last_event_id

    return render(request, "500.html", {
        'sentry_event_id': last_event_id(),
        'sentry_dsn': settings.SENTRY_DSN_API
    }, status=500)
