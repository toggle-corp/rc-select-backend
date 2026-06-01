import typing

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.tool_picker.permission import SteercoUserPermission

from .models import User


class UserCreationForm(forms.ModelForm):  # type: ignore[reportMissingTypeArgument]
    class Meta:
        model = User
        fields = ["email"]


@admin.register(User)
class UserAdmin(DjangoUserAdmin, SteercoUserPermission):  # type: ignore[reportMissingTypeArgument]
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_steerco",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email", "first_name", "last_name")
    add_form = UserCreationForm
    readonly_fields = ("display_name",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "display_name",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_steerco",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email",),
            },
        ),
    )

    @typing.override
    def user_change_password(self, request, id, form_url=""):
        """Superusers or Steerco can reset another user password."""
        if self.is_superuser(request) or self.is_steerco(request):
            return super().user_change_password(request, id, form_url)

        # NOTE: Authenticated non-admin user can reset their own password
        if request.user.is_authenticated and request.user.pk == int(id):
            return super().user_change_password(request, id, form_url)

        messages.error(request, "You do not have permission to perform this action.")
        return HttpResponseRedirect(reverse("admin:user_user_change", args=[id]))
