from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList

UserModel = get_user_model()


class UserModelCreationForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ("email", "password1", "password2")

    def clean_email(self):
        super().clean()
        email = self.cleaned_data.get("email")
        duplicate_emails = UserModel.objects.filter(email=email)
        if duplicate_emails.count() > 0:
            self.errors["email"] = ErrorList()
            self.errors["email"].append(
                "The chosen email address is already registered."
            )
        return email

    def save(self, commit=True):
        user = super().save()
        # Need to have active user for authenticate to succeed
        user.is_active = True
        user.save()
        return user
