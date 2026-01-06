import typing
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_choices_field import IntegerChoicesField
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import UserResource


class Catalog(UserResource):
    """Model representing catalog where a tool belongs to."""

    name = models.CharField[str, str](max_length=200)
    description = models.TextField[str, str]()

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
    description = models.TextField[str, str](blank=True)
    order = models.IntegerField[int, int](default=0, validators=[MinValueValidator(0)])

    # Ordinal-specific fields
    label_na = models.CharField[str, str](max_length=100, default="N/A", blank=True)
    label_1 = models.CharField[str, str](max_length=100, default="1", blank=True)
    label_2 = models.CharField[str, str](max_length=100, default="2", blank=True)
    label_3 = models.CharField[str, str](max_length=100, default="3", blank=True)
    label_4 = models.CharField[str, str](max_length=100, default="4", blank=True)

    # type hints
    options: typing.ClassVar[RelatedManager["CheckboxOption"]]
    get_question_type_display: typing.ClassVar[typing.Callable[[typing.Self], str]]

    class Meta(UserResource.Meta):
        ordering = ["catalog", "order"]
        unique_together = ["catalog", "order"]

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
    order = models.IntegerField[int, int](default=0, validators=[MinValueValidator(0)])

    class Meta(UserResource.Meta):
        ordering = ["question", "order"]
        unique_together = ["question", "order"]

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
        upload_to="logs/",
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

    NOT_AVAILABLE = 10, ("n/a")
    ONE = 11, ("1")
    TWO = 12, ("2")
    THREE = 13, ("3")
    FOUR = 14, ("4")


class ToolAnswer(UserResource):
    """Model representing tool's selection of question and its answer."""

    tool = models.ForeignKey(
        Tool,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    description = models.TextField[str, str]()
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="tool_answers",
    )

    # For ordinal questions
    ordinal_value: int = IntegerChoicesField(  # type: ignore[reportAssignmentType]
        choices_enum=OrdinalTypeEnum,
        blank=True,
        null=True,
    )

    # For checkbox questions
    selected_options = models.ManyToManyField(
        CheckboxOption,
        related_name="tool_answers",
        blank=True,
    )

    class Meta(UserResource.Meta):
        unique_together = ["tool", "question"]
        verbose_name = "Tool Answer"
        verbose_name_plural = "Tool Answers"

    @typing.override
    def __str__(self):
        if self.question.question_type == "ordinal":
            return f"{self.tool.name} - {self.question.title}: {self.ordinal_value}"
        options = ", ".join(
            [opt.text for opt in self.selected_options.all()],
        )
        return f"{self.tool.name} - {self.question.title}: [{options}]"


class UserSubmission(models.Model):
    """Model representing a user's submission of answers for a catalog."""

    id = models.UUIDField[uuid.UUID, uuid.UUID](
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    # type hints
    answers: typing.ClassVar[RelatedManager["UserAnswer"]]
    results: typing.ClassVar[RelatedManager["RecommendationResult"]]

    class Meta(UserResource.Meta):
        ordering = ["-created_at"]
        verbose_name = "User Submission"
        verbose_name_plural = "User Submissions"

    @typing.override
    def __str__(self):
        return f"Submission {self.id} for {self.catalog.name} at {self.created_at}"


class UserAnswer(models.Model):
    """Model representing a user's answer to a specific question."""

    submission = models.ForeignKey(
        UserSubmission,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_answers",
    )

    # For ordinal questions
    ordinal_value: int = IntegerChoicesField(  # type: ignore[reportAssignmentType]
        choices_enum=OrdinalTypeEnum,
        blank=True,
        null=True,
    )

    # For checkbox questions
    selected_options = models.ManyToManyField(
        CheckboxOption,
        related_name="user_answers",
        blank=True,
    )

    class Meta(UserResource.Meta):
        unique_together = ["submission", "question"]
        ordering = ["question__order"]
        verbose_name = "User Answer"
        verbose_name_plural = "User Answers"

    @typing.override
    def __str__(self):
        if self.question.question_type == QuestionTypeEnum.ORDINAL:
            return f"Answer to '{self.question.title}': {self.ordinal_value}"
        options = ", ".join([opt.text for opt in self.selected_options.all()])
        return f"Answer to '{self.question.title}': [{options}]"


class RecommendationResult(models.Model):
    """Model representing recommended tools for a submission."""

    submission = models.ForeignKey(
        UserSubmission,
        on_delete=models.CASCADE,
        related_name="results",
    )
    tool = models.ForeignKey(
        Tool,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )
    rank = models.IntegerField[int, int](
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    score = models.FloatField[float, float](
        help_text="Proximity score - lower is better (closer match)",
    )

    class Meta(UserResource.Meta):
        ordering = ["submission", "rank"]
        unique_together = ["submission", "rank"]
        verbose_name = "Recommendation Result"
        verbose_name_plural = "Recommendation Results"

    @typing.override
    def __str__(self):
        return f"#{self.rank} {self.tool.name} (score: {self.score:.2f})"
