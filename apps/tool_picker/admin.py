import typing

from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.common.admin import UserResourceAdmin

from .models import (
    Catalog,
    CheckboxOption,
    OrdinalTypeEnum,
    Question,
    QuestionTypeEnum,
    RecommendationResult,
    Sector,
    Tool,
    ToolAnswer,
    ToolFeature,
    UserAnswer,
    UserSubmission,
)


class ReadOnlyMixin:
    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False


# Inline for Checkbox Options within Question
class CheckboxOptionInline(admin.TabularInline):  # type: ignore[reportMissingTypeArgument]
    model = CheckboxOption
    extra = 0
    fields = ["order", "text"]
    ordering = ["order"]


# Inline for Ordinal Questions within Catalog
class OrdinalQuestionInline(admin.StackedInline):  # type: ignore[reportMissingTypeArgument]
    model = Question
    extra = 0
    fields = ["order", "title", "description", "question_type", ("label_na", "label_1", "label_2", "label_3", "label_4")]
    ordering = ["order"]
    verbose_name = "Ordinal Question"
    verbose_name_plural = "Ordinal Questions"

    def get_queryset(self, request):  # type: ignore[reportMissingTypeArgument]
        qs = super().get_queryset(request)
        return qs.filter(question_type=QuestionTypeEnum.ORDINAL)


# Inline for Checkbox Questions within Catalog
class CheckboxQuestionInline(admin.StackedInline):  # type: ignore[reportMissingTypeArgument]
    model = Question
    extra = 0
    fields = ["order", "title", "description", "question_type", "edit_options_link"]
    readonly_fields = ["edit_options_link"]
    ordering = ["order"]
    verbose_name = "Checkbox Question"
    verbose_name_plural = "Checkbox Questions"

    def get_queryset(self, request):  # type: ignore[reportMissingTypeArgument]
        qs = super().get_queryset(request)
        return qs.filter(question_type=QuestionTypeEnum.CHECKBOX)

    def formfield_for_dbfield(self, db_field, request, **kwargs) -> forms.Field | None:  # type: ignore[reportMissingTypeArgument]
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and db_field.name == "title":
            formfield.help_text = (
                "Note: To add checkbox options, save this question first, "
                "then click the edit link next to the question to add options."
            )
        return formfield

    @admin.display(description="Add Options")
    def edit_options_link(self, obj):
        """Provide a link to edit options in the bulk admin."""
        if obj and obj.pk:
            url = reverse("admin:tool_picker_checkboxquestionproxy_change", args=[obj.pk])
            return format_html('<a href="{}" target="_blank">Edit Options →</a>', url)
        return "Save question first to add options"


@admin.register(Catalog)
class CatalogAdmin(UserResourceAdmin, admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["name", "question_count", "tool_count", "show_in_help_me_choose"]
    search_fields = ["name", "description"]
    inlines = [OrdinalQuestionInline, CheckboxQuestionInline]

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
        return obj.tool_catalogs.count()


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
    def get_queryset(self, request: typing.Any):
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
    fields = ["question", "ordinal_value", "description"]
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
            # Only show ordinal questions from the tool's catalogs
            _tool_obj = typing.cast("Tool | None", getattr(request, "_tool_obj", None))
            if _tool_obj is not None:
                kwargs["queryset"] = Question.objects.filter(
                    catalog__in=_tool_obj.catalogs.all(),
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
            # Only show checkbox questions from the tool's catalogs
            _tool_obj = typing.cast("Tool | None", getattr(request, "_tool_obj", None))
            if _tool_obj is not None:
                kwargs["queryset"] = Question.objects.filter(
                    catalog__in=_tool_obj.catalogs.all(),
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
    list_display = ["name", "tagline"]
    list_filter = ["catalogs"]
    search_fields = ["name", "tagline", "description"]
    autocomplete_fields = ["catalogs", "tool_sectors", "tool_owners", "tool_features"]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "catalogs",
                    "name",
                    "tagline",
                    "description",
                    "video_link",
                    "tool_link",
                    "tool_sectors",
                    "tool_owners",
                    "tool_features",
                    "logo",
                ),
            },
        ),
    )

    @typing.override
    def get_queryset(self, request: typing.Any):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "tool_sectors",
                "tool_owners",
                "tool_features",
            )
        )

    inlines = [ToolAnswerOrdinalInline, ToolAnswerCheckboxInline]

    @typing.override
    def get_form(self, request, obj=None, change=False, **kwargs):  # type: ignore[reportMissingTypeArgument]
        # Store the tool object in request for use in inlines
        typing.cast("typing.Any", request)._tool_obj = obj
        return super().get_form(request, obj, **kwargs)

    @typing.override
    def save_related(self, request, form, formsets, change):  # type: ignore[reportMissingTypeArgument]
        super().save_related(request, form, formsets, change)

        obj = form.instance

        # Ensure answers exist for ALL questions in ALL selected catalogs
        for catalog in obj.catalogs.all():
            for question in catalog.questions.all():
                tool_answer, created = ToolAnswer.objects.get_or_create(
                    tool=obj,
                    question=question,
                    defaults={
                        "created_by": request.user,
                        "modified_by": request.user,
                        "ordinal_value": (
                            OrdinalTypeEnum.NOT_AVAILABLE if question.question_type == QuestionTypeEnum.ORDINAL else None
                        ),
                    },
                )
                if not created:
                    tool_answer.modified_by = request.user  # type: ignore[reportMissingTypeArgument]
                    tool_answer.save(update_fields=["modified_by"])

        ToolAnswer.objects.filter(tool=obj).exclude(
            question__catalog__in=obj.catalogs.all(),
        ).delete()


# ============================================================================
# User Submission Models Admin
# ============================================================================


class UserAnswerInline(admin.TabularInline):  # type: ignore[reportMissingTypeArgument]
    model = UserAnswer
    extra = 0
    fields = ["question", "ordinal_value", "get_selected_options"]
    readonly_fields = ["get_selected_options"]
    ordering = ["question__order"]

    @admin.display(description="Checkbox Options")
    def get_selected_options(self, obj: UserAnswer):
        if obj.pk and obj.question.question_type == "checkbox":
            return ", ".join([opt.text for opt in obj.selected_options.all()])
        return "-"


class RecommendationResultInline(admin.TabularInline):  # type: ignore[reportMissingTypeArgument]
    model = RecommendationResult
    extra = 0
    fields = ["rank", "tool", "score"]
    ordering = ["rank"]


@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["id", "catalog", "created_at", "answer_count", "recommendation_count"]
    list_filter = ["catalog", "created_at"]
    readonly_fields = ["id", "created_at"]
    fields = ["id", "catalog"]
    inlines = [UserAnswerInline, RecommendationResultInline]

    @admin.display(description="Answers")
    def answer_count(self, obj: UserSubmission):
        return obj.answers.count()

    @admin.display(description="Results")
    def recommendation_count(self, obj: UserSubmission):
        return obj.results.count()


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["submission_id", "question", "question_type", "get_answer"]
    list_filter = ["submission__catalog", "question__question_type"]
    search_fields = ["submission__id", "question__title", "selected_options__id"]
    readonly_fields = ("selected_options",)

    @typing.override
    def get_queryset(self, request):  # type: ignore[reportMissingTypeArgument]
        return super().get_queryset(request).prefetch_related("selected_options")

    def get_fields(self, request, obj=None):  # type: ignore[reportMissingTypeArgument]
        """Show only relevant fields based on question type."""
        base_fields = ["submission", "question"]

        if obj and obj.question.question_type == QuestionTypeEnum.ORDINAL.value:
            return [*base_fields, "ordinal_value"]

        if obj and obj.question.question_type == QuestionTypeEnum.CHECKBOX.value:
            return [*base_fields, "selected_options"]

        return [*base_fields, "ordinal_value", "selected_options"]

    def get_form(self, request, obj=None, **kwargs):  # type: ignore[reportMissingTypeArgument]
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.question.question_type == "checkbox":
            self.filter_horizontal = ["selected_options"]
        else:
            self.filter_horizontal = []
        return form

    @admin.display(description="Submission")
    def submission_id(self, obj: UserAnswer):
        return str(obj.submission.id)[:8] + "..."

    @admin.display(description="Type")
    def question_type(self, obj: UserAnswer):
        return obj.question.get_question_type_display()

    @admin.display(description="Answer")
    def get_answer(self, obj: UserAnswer):
        if obj.question.question_type == QuestionTypeEnum.ORDINAL:
            return obj.ordinal_value or "-"
        options = obj.selected_options.all()
        return ", ".join([opt.text for opt in options]) if options else "(none)"

    def formfield_for_manytomany(self, db_field, request, **kwargs):  # type: ignore[reportMissingTypeArgument]
        if db_field.name == "selected_options":
            user_answer_id = request.resolver_match.kwargs.get("object_id")  # type: ignore[reportOptionsArgumentAccess]
            if user_answer_id:
                try:
                    user_answer = UserAnswer.objects.get(pk=user_answer_id)
                    kwargs["queryset"] = CheckboxOption.objects.filter(question=user_answer.question)
                except UserAnswer.DoesNotExist:
                    pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(RecommendationResult)
class RecommendationResultAdmin(ReadOnlyMixin, admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["submission_short", "rank", "tool", "score", "catalog"]
    list_filter = ["submission__catalog", "rank"]
    search_fields = ["submission__id", "tool__name"]
    ordering = ["submission", "rank"]
    fields = ["submission", "tool", "rank", "score"]

    @admin.display(description="Submission")
    def submission_short(self, obj: RecommendationResult):
        return str(obj.submission.id)[:8] + "..."

    @admin.display(description="Catalog")
    def catalog(self, obj: RecommendationResult):
        return obj.submission.catalog.name


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(ToolFeature)
class ToolFeatureAdmin(admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    list_display = ["name", "feature_category"]
    list_filter = ["feature_category"]
    search_fields = ["name"]
