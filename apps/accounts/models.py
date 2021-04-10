from accounts.managers import AccountManager
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import EmailMessage
from django.db import models


class UserModel(AbstractBaseUser, PermissionsMixin):

    # Basic information
    email = models.EmailField("Email Address", max_length=254, unique=True)
    first_name = models.CharField("First Name", max_length=42)
    last_name = models.CharField("Last Name", max_length=42)

    # Permissions
    is_active = models.BooleanField(
        "Active",
        default=False,
        help_text="Designates whether this user should be treated as "
        "active. Unselect this instead of deleting accounts.",
    )
    is_staff = models.BooleanField(
        "Staff",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_superuser = models.BooleanField("Superuser", default=False)

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="has_changed_accounts",
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    objects = AccountManager()

    USERNAME_FIELD = "email"  # email login rather than arbitrary username
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        name = self.get_full_name()
        if len(name) < 2:
            return self.email
        else:
            return name

    def get_full_name(self):
        full_name = "{0} {1}".format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(
        self, subject, message, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs
    ):
        """Sends an email to this User. Caution, from_email must contain domain
        name in production!"""

        EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[self.email],
            bcc=settings.ADMIN_BCC,
        ).send(fail_silently=False)
