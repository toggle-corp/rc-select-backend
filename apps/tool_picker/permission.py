import typing

from django.contrib import admin

from apps.tool_picker.models import Catalog, Tool, ToolAnswer


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


class SteercoUserPermission(BasePermission):
    @typing.override
    def has_change_permission(self, request, obj=None):
        if self.is_admin(request):
            return True
        if obj is None:
            return request.user.is_authenticated
        return obj.pk == request.user.pk

    @typing.override
    def has_delete_permission(self, request, obj=None):
        return self.is_admin(request)


class ToolPermission(BasePermission):
    @typing.override
    def is_owner(self, request, obj=None):
        user = request.user
        if not user.is_authenticated or obj is None:
            return False
        is_catalog_owner = hasattr(obj, "catalogs") and obj.catalogs.filter(owners=user).exists()
        is_tool_owner = getattr(obj, "created_by_id", None) == user.pk or (
            hasattr(obj, "owners") and obj.owners.filter(pk=user.pk).exists()
        )
        return is_catalog_owner or is_tool_owner

    @typing.override
    def has_add_permission(self, request):
        if self.is_admin(request):
            return True
        # Catalog owners can add tools
        user = request.user
        if user.is_authenticated:
            return Catalog.objects.filter(owners=user).exists()
        return False

    @typing.override
    def has_change_permission(self, request, obj=None):
        if self.is_admin(request):
            return True
        if obj is None:
            return request.user.is_authenticated
        return self.is_owner(request, obj)


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

    def _resolve_catalog(self, obj):
        """Resolve the parent Catalog regardless of what obj is.
        - has_add_permission   → obj is the parent (Catalog or Tool).
        - has_change/delete    → obj is the inline instance.
        """
        if obj is None:
            return None

        if isinstance(obj, Catalog):
            return obj
        if isinstance(obj, Tool):
            return obj

        # if obj is a Question inline instance
        if hasattr(obj, "catalog"):
            return obj.catalog

        if hasattr(obj, "question") and hasattr(obj.question, "catalog"):
            return obj.question.catalog

        return None

    def _has_write_access(self, request, obj) -> bool:
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or getattr(user, "is_steerco", False):
            return True

        if obj is None:
            tool_obj = getattr(request, "_tool_obj", None)
            if tool_obj is not None:
                is_tool_owner = (
                    getattr(tool_obj, "created_by_id", None) == user.pk or tool_obj.owners.filter(pk=user.pk).exists()
                )
                if is_tool_owner:
                    return True
            return Catalog.objects.filter(owners=user).exists()

        # NOTE: if obj is a Tool — Django passes the parent Tool during inline render so we need to
        # Check BOTH catalog ownership and tool ownership
        if isinstance(obj, Tool):
            is_tool_owner = getattr(obj, "created_by_id", None) == user.pk or obj.owners.filter(pk=user.pk).exists()
            if is_tool_owner:
                return True
            return obj.catalogs.filter(owners=user).exists()

        if isinstance(obj, ToolAnswer):
            parent_tool = obj.tool
            is_tool_owner = (
                getattr(parent_tool, "created_by_id", None) == user.pk or parent_tool.owners.filter(pk=user.pk).exists()
            )
            if is_tool_owner:
                return True
            return parent_tool.catalogs.filter(owners=user).exists()

        # Fallback for any other inline model
        resolved = self._resolve_catalog(obj)
        is_catalog_owner = (
            resolved is not None and hasattr(resolved, "owners") and resolved.owners.filter(pk=user.pk).exists()
        )
        is_creator = getattr(obj, "created_by_id", None) == user.pk
        is_direct_owner = hasattr(obj, "owners") and obj.owners.filter(pk=user.pk).exists()
        return is_catalog_owner or is_creator or is_direct_owner


class CaseStudyPermission(BasePermission):
    @typing.override
    def is_owner(self, request, obj=None):
        user = request.user
        if not user.is_authenticated or obj is None:
            return False
        # Owner of the case study = owner of the related tool
        return obj.tool.owners.filter(pk=user.pk).exists()

    @typing.override
    def has_add_permission(self, request):
        if self.is_admin(request):
            return True
        user = request.user
        if user.is_authenticated:
            return Tool.objects.filter(owners=user).exists()
        return False

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
