# Register your models here.
import typing

from django.contrib import admin
from django.db.models import Q

from apps.resources.models import CaseStudy, ContactRequest, RequestDemo
from apps.tool_picker.admin import ReadOnlyMixin
from apps.tool_picker.models import Tool
from apps.tool_picker.permission import CaseStudyPermission


@admin.register(ContactRequest)
class ContactRequestAdmin(ReadOnlyMixin, admin.ModelAdmin[ContactRequest]):
    list_display = ("name", "email", "national_society", "created_at")
    search_fields = ("name", "email")


@admin.register(CaseStudy)
class CaseStudyAdmin(CaseStudyPermission):
    list_display = ("title",)
    search_fields = ("title",)
    list_select_related = ("tool",)
    autocomplete_fields = ("tool",)
    readonly_fields = ("created_by", "modified_by")

    exclude = ("created_by", "modified_by")  # NOTE: Prevent admin form validation errors

    @typing.override
    def save_model(self, request, obj, form, change):
        """Automatically set created_by and modified_by in admin."""
        if not obj.pk:
            obj.created_by = request.user

        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    @typing.override
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.is_admin(request):
            return qs
        user = request.user
        return qs.filter(
            Q(tool__owners=user) | Q(tool__created_by=user) | Q(tool__catalogs__owners=user),
        ).distinct()

    @typing.override
    def get_form(self, request, obj=None, **kwargs):  # type: ignore[reportMissingTypeArgument]
        form = super().get_form(request, obj, **kwargs)
        if not self.is_admin(request) and "tool" in form.base_fields:
            user = request.user
            form.base_fields["tool"].queryset = Tool.objects.filter(  # type: ignore[reportMissingTypeArgument]
                Q(owners=user) | Q(created_by=user) | Q(catalogs__owners=user),
            ).distinct()
        return form


@admin.register(RequestDemo)
class RequestDemoAdmin(ReadOnlyMixin, admin.ModelAdmin[RequestDemo]):
    list_display = ("name", "email", "national_society", "created_at")
    search_fields = ("name", "email")
