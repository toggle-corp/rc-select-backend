import typing

from django.contrib import admin


class BasePermission(admin.ModelAdmin):
    def is_superuser(self, request):
        return request.user.is_authenticated and request.user.is_superuser

    def is_steerco(self, request):
        return request.user.is_authenticated and getattr(request.user, "is_steerco", False)

    def is_admin(self, request):
        return self.is_superuser(request) or self.is_steerco(request)

    def is_owner(self, request, obj=None):
        return False

    @typing.override
    def has_module_permission(self, request):
        return request.user.is_authenticated

    @typing.override
    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    @typing.override
    def has_add_permission(self, request):
        return self.is_admin(request)

    @typing.override
    def has_change_permission(self, request, obj=None):
        if self.is_admin(request):
            return True
        if obj is None:
            return request.user.is_authenticated
        return self.is_owner(request, obj)

    @typing.override
    def has_delete_permission(self, request, obj=None):
        if self.is_admin(request):
            return True
        if obj is None:
            return request.user.is_authenticated
        return self.is_owner(request, obj)


class CatalogPermission(BasePermission):
    @typing.override
    def is_owner(self, request, obj=None):
        user = request.user
        if not user.is_authenticated or obj is None:
            return False
        return hasattr(obj, "owners") and obj.owners.filter(pk=user.pk).exists()


class ToolPermission(BasePermission):
    @typing.override
    def is_owner(self, request, obj=None):
        user = request.user
        if not user.is_authenticated or obj is None:
            return False

        is_catalog_owner = (
            hasattr(obj, "catalog") and hasattr(obj.catalog, "owners") and obj.catalog.owners.filter(pk=user.pk).exists()
        )

        is_tool_owner = getattr(obj, "created_by_id", None) == user.pk or (
            hasattr(obj, "owners") and obj.owners.filter(pk=user.pk).exists()
        )

        return is_catalog_owner or is_tool_owner


class SteercoUserPermission(BasePermission):
    @typing.override
    def has_change_permission(self, request, obj=None):
        return self.is_admin(request)

    @typing.override
    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


class InlineAdminPermission(admin.TabularInline):
    @typing.override
    def has_view_permission(self, request, obj=None) -> bool:
        return request.user.is_authenticated

    @typing.override
    def has_add_permission(self, request, obj=None) -> bool:
        return self._has_write_access(request, obj)

    @typing.override
    def has_change_permission(self, request, obj=None) -> bool:
        return self._has_write_access(request, obj)

    @typing.override
    def has_delete_permission(self, request, obj=None) -> bool:
        return self._has_write_access(request, obj)

    def _has_write_access(self, request, obj) -> bool:
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or getattr(user, "is_steerco", False):
            return True
        if obj is None:
            return False

        # Catalog owner of the parent OR direct owner/creator
        is_catalog_owner = hasattr(obj, "owners") and obj.owners.filter(pk=user.pk).exists()
        is_creator = getattr(obj, "created_by_id", None) == user.pk
        return is_catalog_owner or is_creator
