import typing

# make a base admin class for auto created by and modified by
from django.contrib import admin


class UserResourceAdmin(admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    readonly_fields = (
        "created_by",
        "modified_by",
    )

    @typing.override
    def save_model(self, request, obj, form, change):  # type: ignore[reportMissingTypeArgument]
        """Automatically set created_by and modified_by in admin."""
        if not obj.pk:  # new object
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    @typing.override
    def save_formset(self, request, form, formset, change) -> None:  # type: ignore[reportMissingTypeArgument]
        instances = formset.save(commit=False)
        for obj in instances:
            if not obj.pk and hasattr(obj, "created_by_id"):
                obj.created_by = request.user
            if hasattr(obj, "modified_by_id"):
                obj.modified_by = request.user
            obj.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()
