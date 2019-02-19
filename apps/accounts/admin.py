from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from accounts.models import UserModel
from utils import export_to_xls


@admin.register(UserModel)
class UserModelAdmin(UserAdmin):
    list_display = (
        "email", "first_name", "last_name", "is_active", "date_created",
    )
    list_filter = ("is_active", "is_staff", "is_superuser",)
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_created",)
    readonly_fields = ("last_login", "date_created", "last_updated_by",)
    actions = ("send_password_reset", "export_to_xls")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser",
            "groups", "user_permissions")}),
        ("Meta", {"fields": ("last_login", "date_created", "last_updated_by")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2")}
        ),
    )

    def send_password_reset(self, request, queryset):
        for user in queryset:
            try:
                validate_email( user.email )
                form = PasswordResetForm(data={"email": user.email})
                form.is_valid()

                form.save(email_template_name="accounts/password_forced_reset_email.html",
                          extra_email_context={ "full_name": user.get_full_name() })
                self.message_user(request, "Succesfully sent password reset email.")
            except ValidationError:
                self.message_user(request, "User does not have a valid email address", level="error")
    send_password_reset.short_description = "Send password reset link"

    def export_to_xls(self, request, queryset):
        return export_to_xls(request, queryset)
    export_to_xls.short_description = "Export selected users to xls"

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        obj.save()

    def history_view(self, request, object_id, extra_context=None):
        """ Hack the history view such that it renders html """
        s = super(UserModelAdmin, self).history_view(request, object_id, extra_context=None)
        action_list = s.context_data["action_list"]
        for log_entry in action_list:
            try:
                log_entry.change_message = format_html(log_entry.change_message)
            except KeyError:
                pass
        return s

admin.site.unregister(Group)
