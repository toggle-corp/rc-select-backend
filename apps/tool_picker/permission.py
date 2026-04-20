import typing

from django.contrib import admin
from django.http import HttpRequest


class BasePermission(admin.ModelAdmin):
    pass


class AdminPermission(BasePermission):
    def is_steerco_or_is_superuser(self, request: HttpRequest) -> bool:
        user = request.user
        return user.is_authenticated and (user.is_superuser or getattr(user, "is_steerco", False))

    def is_owner_or_creator(self, request: HttpRequest, obj) -> bool:
        user = request.user

        if not user.is_authenticated or obj is None:
            return False

        return obj.created_by_id == user.pk or obj.owners.filter(pk=user.pk).exists()

    @typing.override
    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_authenticated

    @typing.override
    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_authenticated

    @typing.override
    def has_add_permission(self, request: HttpRequest) -> bool:
        return self.is_steerco_or_is_superuser(request)

    @typing.override
    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        if self.is_steerco_or_is_superuser(request):
            return True

        if obj is None:
            return request.user.is_authenticated

        return self.is_owner_or_creator(request, obj)

    @typing.override
    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        if self.is_steerco_or_is_superuser(request):
            return True

        if obj is None:
            return request.user.is_authenticated

        return self.is_owner_or_creator(request, obj)


class InlineAdminPermission(admin.TabularInline):
    @typing.override
    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_authenticated

    @typing.override
    def has_add_permission(self, request, obj=None):
        return self.parent_has_access(request, obj)

    @typing.override
    def has_change_permission(self, request, obj=None):
        return self.parent_has_access(request, obj)

    @typing.override
    def has_delete_permission(self, request, obj=None):
        return self.parent_has_access(request, obj)

    def parent_has_access(self, request, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser or getattr(user, "is_steerco", False):
            return True

        if obj is None:
            return False

        return obj.created_by_id == user.id or obj.owners.filter(pk=user.pk).exists()
