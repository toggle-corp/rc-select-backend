import typing

from django.contrib import admin

from apps.common.admin import UserResourceAdmin

from .models import (
    Catalog,
    CheckboxOption,
    OrdinalTypeEnum,
    Question,
    QuestionTypeEnum,
    Tool,
    ToolAnswer,
)


# Inline for CheckboxOptions within Question
class CheckboxOptionInline(admin.TabularInline):  # type: ignore[reportMissingTypeArgument]
    model = CheckboxOption
    extra = 0
    fields = ["order", "text"]
    ordering = ["order"]


# Inline for Questions within Catalog
class QuestionInline(admin.StackedInline):  # type: ignore[reportMissingTypeArgument]
    model = Question
    extra = 0
    fields = ["order", "question_type", "title", "description", ("label_na", "label_1", "label_2", "label_3", "label_4")]
    ordering = ["order"]
    show_change_link = True


# Inline for Tools within Catalog
class ToolInline(admin.TabularInline):  # type: ignore[reportMissingTypeArgument]
    model = Tool
    extra = 0
    fields = ["name", "tagline"]
    show_change_link = True


@admin.register(Catalog)
class CatalogAdmin(UserResourceAdmin, admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["name", "question_count", "tool_count"]
    search_fields = ["name", "description"]
    inlines = [QuestionInline, ToolInline]

    @admin.display(description="Questions")
    def question_count(self, obj: Catalog):
        ordinal = obj.questions.filter(
            question_type=QuestionTypeEnum.ORDINAL,
        ).count()
        checkbox = obj.questions.filter(
            question_type=QuestionTypeEnum.CHECKBOX,
        ).count()
        return f"{obj.questions.count()} ({ordinal} ordinal, {checkbox} checkbox)"

    @admin.display(description="Tools")
    def tool_count(self, obj: Catalog):
        return obj.tools.count()


@admin.register(Question)
class QuestionAdmin(UserResourceAdmin, admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = [
        "title",
        "catalog",
        "question_type",
        "order",
        "option_count",
    ]
    list_filter = ["catalog", "question_type"]
    search_fields = ["title", "description"]
    ordering = ["catalog", "order"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "catalog",
                    "order",
                    "question_type",
                    "title",
                    "description",
                ),
            },
        ),
        (
            "Ordinal Scale Labels (for ordinal questions only)",
            {
                "fields": (("label_na", "label_1", "label_2", "label_3", "label_4"),),
                "classes": ("collapse",),
                "description": 'These fields are only \
                used when question_type is "ordinal"',
            },
        ),
    )
    inlines = [CheckboxOptionInline]

    @admin.display(description="Options")
    def option_count(self, obj: Question):
        if obj.question_type == QuestionTypeEnum.CHECKBOX:
            return obj.options.count()
        return "-"

    @typing.override
    def get_inline_instances(self, request, obj=None):  # type: ignore[reportMissingTypeArgument]
        """Only show CheckboxOptionInline for checkbox questions."""
        if obj and obj.question_type == QuestionTypeEnum.CHECKBOX:
            return super().get_inline_instances(request, obj)
        return []

    @typing.override
    def save_model(self, request, obj, form, change):  # type: ignore[reportMissingTypeArgument]
        """Automatically set created_by and modified_by in admin."""
        if not obj.pk:  # new object
            obj.created_by = request.user
            obj.modified_by = request.user
        super().save_model(request, obj, form, change)


# Proxy model for checkbox-only view
class CheckboxQuestionProxy(Question):
    class Meta(Question.Meta):
        proxy = True
        verbose_name = "Checkbox Question (Bulk Edit)"
        verbose_name_plural = "Checkbox Questions (Bulk Edit)"


@admin.register(CheckboxQuestionProxy)
class CheckboxQuestionBulkAdmin(UserResourceAdmin, admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["title", "catalog", "order", "option_count", "option_list"]
    list_filter = ["catalog"]
    search_fields = ["title", "description"]
    ordering = ["catalog", "order"]

    inlines = [CheckboxOptionInline]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("catalog", "order", "title", "description"),
            },
        ),
    )

    @typing.override
    def get_queryset(self, request):  # type: ignore[reportMissingTypeArgument]
        """Only show checkbox questions."""
        qs = super().get_queryset(request)
        return qs.filter(question_type=QuestionTypeEnum.CHECKBOX)

    @admin.display(description="# Options")
    def option_count(self, obj: Question):
        return obj.options.count()

    @admin.display(description="Options")
    def option_list(self, obj: Question):
        options = obj.options.all()[:5]  # Show first 5
        text = ", ".join([opt.text for opt in options])
        if obj.options.count() > 5:
            text += f" ... (+{obj.options.count() - 5} more)"
        return text or "(no options)"

    @typing.override
    def has_add_permission(self, request):  # type: ignore[reportMissingTypeArgument]
        """Prevent adding from this view - use main Question admin."""
        return False

    @typing.override
    def save_model(self, request, obj, form, change):  # type: ignore[reportMissingTypeArgument]
        """Ensure question_type is always checkbox."""
        obj.question_type = QuestionTypeEnum.CHECKBOX
        super().save_model(request, obj, form, change)


# Separate inlines for different answer types
class ToolAnswerOrdinalInline(admin.TabularInline):  # type: ignore[reportMissingTypeArgument]
    model = ToolAnswer
    extra = 0
    fields = ["question", "ordinal_value"]
    ordering = ["question__order"]
    can_delete = False
    verbose_name = "Ordinal Answer"
    verbose_name_plural = "Ordinal Answers"

    @typing.override
    def get_queryset(self, request):  # type: ignore[reportMissingTypeArgument]
        qs = super().get_queryset(request)
        return qs.filter(question__question_type=QuestionTypeEnum.ORDINAL)

    @typing.override
    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # type: ignore[reportMissingTypeArgument]
        if db_field.name == "question":
            # Only show ordinal questions from the tool's catalog
            _tool_obj = typing.cast(Tool | None, getattr(request, "_tool_obj", None))
            if _tool_obj is not None:
                kwargs["queryset"] = Question.objects.filter(
                    catalog=_tool_obj.catalog,
                    question_type=QuestionTypeEnum.ORDINAL,
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ToolAnswerCheckboxInline(admin.StackedInline):  # type: ignore[reportMissingTypeArgument]
    model = ToolAnswer
    extra = 0
    fields = ["question", "selected_options"]
    filter_horizontal = ["selected_options"]
    ordering = ["question__order"]
    can_delete = False
    verbose_name = "Checkbox Answer"
    verbose_name_plural = "Checkbox Answers"

    @typing.override
    def get_queryset(self, request):  # type: ignore[reportMissingTypeArgument]
        qs = super().get_queryset(request)
        return qs.filter(question__question_type=QuestionTypeEnum.CHECKBOX)

    @typing.override
    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # type: ignore[reportMissingTypeArgument]
        if db_field.name == "question":
            # Only show checkbox questions from the tool's catalog
            _tool_obj = typing.cast(Tool | None, getattr(request, "_tool_obj", None))
            if _tool_obj is not None:
                kwargs["queryset"] = Question.objects.filter(
                    catalog=_tool_obj.catalog,
                    question_type=QuestionTypeEnum.CHECKBOX,
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @typing.override
    def formfield_for_manytomany(self, db_field, request, **kwargs):  # type: ignore[reportMissingTypeArgument]
        if db_field.name == "selected_options":
            # Dynamically filter options based on the question
            # This will be handled by JavaScript or manual selection
            pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Tool)
class ToolAdmin(UserResourceAdmin, admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["name", "catalog", "tagline"]
    list_filter = ["catalog"]
    search_fields = ["name", "tagline", "description"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("catalog", "name", "tagline", "description"),
            },
        ),
    )

    inlines = [ToolAnswerOrdinalInline, ToolAnswerCheckboxInline]

    @typing.override
    def get_form(self, request, obj=None, change=False, **kwargs):  # type: ignore[reportMissingTypeArgument]
        # Store the tool object in request for use in inlines
        typing.cast(typing.Any, request)._tool_obj = obj
        return super().get_form(request, obj, **kwargs)

    @typing.override
    def save_model(self, request, obj, form, change):  # type: ignore[reportMissingTypeArgument]
        """After saving tool, auto-create answer entries for all questions in the catalog."""
        super().save_model(request, obj, form, change)

        for question in obj.catalog.questions.all():
            ToolAnswer.objects.get_or_create(
                tool=obj,
                created_by=request.user,
                modified_by=request.user,
                question=question,
                defaults={
                    "ordinal_value": OrdinalTypeEnum.NOT_AVAILABLE
                    if question.question_type == QuestionTypeEnum.ORDINAL
                    else None,
                },
            )
