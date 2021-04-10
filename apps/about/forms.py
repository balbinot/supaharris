import copy

from django import forms
from django.conf import settings
from tinymce.widgets import TinyMCE


class FixTinyMCEHasTooWideUIForm(forms.ModelForm):
    tinymce = copy.copy(settings.TINYMCE_MINIMAL_CONFIG)
    tinymce["width"] = "calc(100% - 170px)"
    tinymce["height"] = "200"
    content = forms.CharField(widget=TinyMCE(mce_attrs=tinymce), required=False)

    def __init__(self, *args, **kwargs):
        super(FixTinyMCEHasTooWideUIForm, self).__init__(*args, **kwargs)
