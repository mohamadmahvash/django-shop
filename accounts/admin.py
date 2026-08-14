from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User, OtpCode


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["email", "phone_number", "is_admin", "last_login"]
    list_filter = ["is_admin"]

    add_fieldsets = [
        [None, {"fields": ["full_name", "email", "phone_number", "password1", "password2"]}],
    ]

    search_fields = ["email", "full_name", "phone_number"]
    ordering = ["full_name"]
    filter_horizontal = ["groups", "user_permissions"]

    def get_fieldsets(self, request, obj=None):

        if request.user.is_superuser:
            return (
                (None, {
                    "fields": (
                        "full_name",
                        "email",
                        "phone_number",
                        "password",
                    )
                }),
                ("Permissions", {
                    "fields": (
                        "is_active",
                        "is_admin",
                        "last_login",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    )
                }),
            )

        return (
            (None, {
                "fields": (
                    "full_name",
                    "email",
                    "phone_number",
                    "password",
                )
            }),
            ("Permissions", {
                "fields": (
                    "is_active",
                    "is_admin",
                    "last_login",
                    "is_superuser",
                )
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        readonly = ["last_login"]

        if not request.user.is_superuser:
            readonly.append("is_superuser")

        return readonly

    def response_change(self, request, obj):
        if '_saveupper' in request.POST:
            obj.full_name = obj.full_name.upper()
            obj.save()
            self.message_user(request, "full name save uppercase!", "success")
            return redirect("admin:accounts_user_changelist")
        return super().response_change(request, obj)


admin.site.register(User, UserAdmin)


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ["phone_number", 'code', 'created_at']
