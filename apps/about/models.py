from django.db import models
from django.utils import timezone

from tinymce.models import HTMLField


class ContactInfo(models.Model):
    webmaster_email_address = models.EmailField()

    def __str__(self):
        return self.webmaster_email_address


class PrivacyPolicy(models.Model):
    # TODO: perhaps make this immutable because it is required to store previous
    # privacy policy versions for GDPR. If it cannot be modified it would force
    # the user to create a new policy every time (even for typos though).

    title = models.CharField(max_length=64, default="Privacy Policy")
    content = HTMLField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} of {1}".format(self.title,
            timezone.datetime.strftime(self.date, "%Y-%m-%d"))
