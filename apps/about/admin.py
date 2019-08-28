import copy

from django import forms
from django.contrib import admin
from django.conf import settings

from tinymce.widgets import TinyMCE

from about.models import ContactInfo
from about.models import PrivacyPolicy
from about.forms import FixTinyMCEHasTooWideUIForm


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        add_permission = super().has_add_permission(request)
        if ContactInfo.objects.count() >= 1:
            add_permission = False
        return add_permission


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    form = FixTinyMCEHasTooWideUIForm
