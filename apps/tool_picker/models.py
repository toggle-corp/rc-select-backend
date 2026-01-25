import typing

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django_choices_field import IntegerChoicesField
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import UserResource


class Catalog(UserResource):
    """Model representing catalog where a tool belongs to."""

    name = models.CharField[str, str](max_length=200)
    description = models.TextField[str, str]()
    show_in_help_me_choose = models.BooleanField[bool | None, bool | None](default=False)

    # type hints
    questions: typing.ClassVar[RelatedManager["Question"]]
    tools: typing.ClassVar[RelatedManager["Tool"]]

    class Meta(UserResource.Meta):
        ordering = ["name"]

    @typing.override
    def __str__(self):
        return self.name


class QuestionTypeEnum(models.IntegerChoices):
    """Enum representing type of question."""

    ORDINAL = 10, ("Ordinal")
    CHECKBOX = 20, ("Checkbox")


class Question(UserResource):
    """Model representing question within a catalog."""

    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_type: int = IntegerChoicesField(  # type: ignore[reportAssignmentType]
        choices_enum=QuestionTypeEnum,
    )
    title = models.CharField[str, str](max_length=500)
    short_name = models.CharField[str, str](max_length=500)
    description = models.TextField[str, str](blank=True)
    order = models.IntegerField[int, int](default=1, validators=[MinValueValidator(1)])

    # Ordinal-specific fields
    label_na = models.TextField[str, str](default="N/A", blank=True)
    label_1 = models.TextField[str, str](default="1", blank=True)
    label_2 = models.TextField[str, str](default="2", blank=True)
    label_3 = models.TextField[str, str](default="3", blank=True)
    label_4 = models.TextField[str, str](default="4", blank=True)

    # type hints
    options: typing.ClassVar[RelatedManager["CheckboxOption"]]
    get_question_type_display: typing.ClassVar[typing.Callable[[typing.Self], str]]

    class Meta(UserResource.Meta):
        UniqueConstraint(fields=["catalog", "order"], name="unique_catalog_order")
        ordering = ["catalog", "order"]

    @typing.override
    def __str__(self) -> str:
        return f"{self.catalog.name} - [{self.get_question_type_display()}] {self.title}"


class CheckboxOption(UserResource):
    """Model representing option of checkbox question."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
    )
    text = models.CharField[str, str](max_length=300)
    order = models.IntegerField[int, int](default=1, validators=[MinValueValidator(1)])

    class Meta(UserResource.Meta):
        ordering = ["question", "order"]
        UniqueConstraint(fields=["question", "order"], name="unique_question_order")

    @typing.override
    def __str__(self):
        return f"{self.question.title} - {self.text}"


class Tool(UserResource):
    """Model representing tool."""

    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name="tools",
    )
    name = models.CharField[str, str](max_length=200)
    tagline = models.CharField[str, str](max_length=300, blank=True)
    description = models.TextField[str, str]()
    video_link = models.CharField[str, str](blank=True, null=True)
    tool_link = models.CharField[str, str](blank=True, null=True)
    logo = models.ImageField(
        upload_to="logos/",
        verbose_name="Logo",
        null=True,
        blank=True,
    )

    class Meta(UserResource.Meta):
        ordering = ["catalog", "name"]

    @typing.override
    def __str__(self):
        return f"{self.name} ({self.catalog.name})"


class OrdinalTypeEnum(models.IntegerChoices):
    """Enum representing scale of ordinal type question."""

    NOT_AVAILABLE = 10, ("N/A")
    ONE = 11, ("One")
    TWO = 12, ("Two")
    THREE = 13, ("Three")
    FOUR = 14, ("Four")


class BaseAnswer(models.Model):
    """Base model for the Answer."""

    question = models.ForeignKey[Question, Question](
        Question,
        on_delete=models.CASCADE,
        related_name="+",
    )
    ordinal_value: int = IntegerChoicesField(  # type: ignore[reportAssignmentType]
        choices_enum=OrdinalTypeEnum,
        blank=True,
        null=True,
    )
    selected_options = models.ManyToManyField(
        CheckboxOption,
        related_name="+",
        blank=True,
    )
    get_ordinal_value_display: typing.ClassVar[typing.Callable[[typing.Self], str]]

    class Meta:
        abstract = True


class ToolAnswer(BaseAnswer, UserResource):
    """Model representing Tool Answer."""

    tool = models.ForeignKey[Tool, Tool](
        Tool,
        on_delete=models.CASCADE,
        related_name="tool_answer",
    )
    description = models.TextField()

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        UniqueConstraint(fields=["tool", "question"], name="unique_tool_question")
        verbose_name = "Tool Answer"
        verbose_name_plural = "Tool Answers"

    @typing.override
    def __str__(self):
        if self.question.question_type == QuestionTypeEnum.ORDINAL.value:
            return f"{self.tool.name} - {self.question.title}: {self.ordinal_value}"
        options = ", ".join(
            [opt.text for opt in self.selected_options.all()],
        )
        return f"{self.tool.name} - {self.question.title}: [{options}]"


class UserAnswer(BaseAnswer):
    """Model Representing User Answer."""

    catalog = models.ForeignKey[Catalog, Catalog](
        Catalog,
        on_delete=models.CASCADE,
        related_name="catalog_answer",
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = "User Answer"
        verbose_name_plural = "User Answers"

    @typing.override
    def __str__(self):
        if self.question.question_type == QuestionTypeEnum.ORDINAL.value:
            return f"Answer to '{self.question.title}': {self.ordinal_value}"
        options = ", ".join([opt.text for opt in self.selected_options.all()])
        return f"Answer to '{self.question.title}': [{options}]"


class RecommendationResult(models.Model):
    """Model representing recommended tools for a submission."""

    catalog = models.ForeignKey[Catalog, Catalog](
        Catalog,
        related_name="catalog_recommendation_result",
        on_delete=models.CASCADE,
        null=True,
    )
    tool = models.ForeignKey(
        Tool,
        on_delete=models.CASCADE,
        related_name="tool_recommendation_result",
    )
    rank = models.IntegerField[int, int](
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    score = models.FloatField[float, float](
        help_text="Proximity score - lower is better (closer match)",
    )

    class Meta(UserResource.Meta):
        ordering = ["rank"]
        verbose_name = "Recommendation Result"
        verbose_name_plural = "Recommendation Results"

    @typing.override
    def __str__(self):
        return f"#{self.rank} {self.tool.name} (score: {self.score:.2f})"
