from django.forms.utils import ErrorList
from django.contrib.auth.forms import (UserChangeForm, UserCreationForm)

from django.contrib.auth import get_user_model
UserModel = get_user_model()

class UserModelCreationForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ("email",)

    def clean_email(self):
        super().clean()
        email = self.cleaned_data.get("email")
        duplicate_emails = UserModel.objects.filter(email=email)
        if len(duplicate_emails) > 0:
            self.errors["email"] = ErrorList()
            self.errors["email"].append("The chosen email address is already registered.")
        return email
