from django.db import models


class ContactInfo(models.Model):
    webmaster_email_address = models.EmailField()
