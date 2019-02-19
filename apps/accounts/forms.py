import sys

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator

from .models import UserModel


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=256, label="Email", required=True,
        widget=forms.TextInput(attrs={"class": "form-control sign-up-field", "placeholder": "Emailadres"}))
    first_name = forms.CharField(max_length=42, label="First Name", required=True,
        widget=forms.TextInput(attrs={"class": "form-control sign-up-field", "placeholder": "First Name"}))
    last_name = forms.CharField(max_length=42, label="Last Name", required=True,
        widget=forms.TextInput(attrs={"class": "form-control sign-up-field", "placeholder": "Last Name"}))
    password1 = forms.CharField(label="Password", strip=False,
        widget=forms.PasswordInput(attrs={"class":"form-control sign-up-field", "placeholder": "Password"}),
        help_text=password_validation.password_validators_help_text_html()
    )
    password2 = forms.CharField(label="Password confirmation", strip=False,
        widget=forms.PasswordInput(attrs={"class":"form-control sign-up-field", "placeholder": "Password (again)"}),
        help_text="Enter the same password as before, for verification."
    )

    accept_terms = forms.BooleanField(required=True, label="Accept",
        widget=forms.CheckboxInput(attrs={"id": "privacy-true", "class": "checkbox", "type": "checkbox"}))

    class Meta:
        model = UserModel
        fields = ("email", "first_name", "last_name", "password1", "password2",)


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, label="Email Address", required=True,
        widget=forms.TextInput(attrs={"class":"form-control sign-up-field", "placeholder": "Emailadres"}))
    first_name = forms.CharField(max_length=30, label="First Name", required=True,
        widget=forms.TextInput(attrs={"class":"form-control sign-up-field", "placeholder": "First Name"}))
    last_name = forms.CharField(max_length=30, label="Last Name", required=True,
        widget=forms.TextInput(attrs={"class":"form-control sign-up-field", "placeholder": "Last Name"}))

    class Meta:
        model = UserModel
        fields = ( "email", "first_name", "last_name" )


class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254, label="Email Address", required=True,
        widget=forms.TextInput(attrs={"class": "form-control sign-up-field", "placeholder": "Email Address"}))

    def save(self, domain_override=None,
             subject_template_name="accounts/password_reset_subject.txt",
             email_template_name="accounts/password_reset_email.html",
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """ Generate a one-use only link for resetting password and send it to the user. """

        email = self.cleaned_data["email"]
        user = UserModel.objects.filter(email=email).first()

        # Here we hack the PasswordResetForm to notify user if no account with the email address is known
        # Do we want this? This way one could brute-force email addresses to see if they"re known in our db?
        if user is not None:
            super(PasswordResetForm, self).save(
                domain_override=domain_override, subject_template_name=subject_template_name,
                email_template_name=email_template_name, use_https=use_https,
                token_generator=token_generator, from_email=from_email, request=request,
                html_email_template_name=html_email_template_name,
                extra_email_context=extra_email_context)
        else:
            # TODO: take action for unknown email address
            print("Uh oh email address not known")


class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"class": "form-control sign-up-field",
            "placeholder": "Password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control sign-up-field",
            "placeholder": "New password (again)"}),
    )


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": "Your old password was entered incorrectly. Please enter it again.",
    }
    old_password = forms.CharField(
        label="Old password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autofocus": True, "class": "form-control sign-up-field",
            "placeholder": "Old password"}),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password


class DeleteAccountForm(forms.Form):
    email = forms.EmailField(max_length=254, label="Email Address", required=True,
        widget=forms.TextInput(attrs={"class": "form-control sign-up-field", "placeholder": "Type emailadres to confirm"}))
