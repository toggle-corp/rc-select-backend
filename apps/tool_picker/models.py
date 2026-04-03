import re
import typing
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_choices_field import IntegerChoicesField
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import UserResource
from apps.user.models import User

# NOTE: regex source https://gist.github.com/Mecanik/b339e629c1020fcddbf7df5fadf305b1

REGEX_PATTERN = re.compile(r"^((?:https?:)?\/\/)?((?:www|player|m)\.)?(vimeo\.com|youtube\.com|youtu\.be).*$")


def validate_url(url: str) -> None:
    """Validates that the URL is a YouTube or Vimeo video link.

    Args:
        url: The video URL to check.

    Raises:
        ValidationError: If the URL is any link other than YouTube or Vimeo.

    """
    if not REGEX_PATTERN.match(url):
        raise ValidationError(
            "Only YouTube or Vimeo video links are allowed.",
        )


class Catalog(UserResource):
    """Model representing catalog where a tool belongs to."""

    name = models.CharField[str, str](max_length=200)
    description = models.TextField[str, str]()
    show_in_help_me_choose = models.BooleanField[bool | None, bool | None](default=False)

    # type hints
    questions: typing.ClassVar[RelatedManager["Question"]]
    tool_catalogs: typing.ClassVar[RelatedManager["Tool"]]

    class Meta(UserResource.Meta):
        ordering = ["name"]

    @typing.override
    def __str__(self):
        return self.name


class ToolFeature(models.Model):
    """Model representing a tool feature."""

    class FeatureCategoryEnum(models.IntegerChoices):
        """Enum representing feature category."""

        CONFIGURATION = 10, ("Configuration")
        BENEFICIARY_REGISTRATION = 20, ("Beneficiary Registration")
        DISTRIBUTION_MANAGEMENT = 30, ("Distribution Management")
        FEEDBACK_AND_SURVEYS = 40, ("Feedback and Surveys")
        DATA_MANAGEMENT = 50, ("Data Management")
        REPORTING_AND_ANALYTICS = 60, ("Reporting and Analytics")

    name = models.CharField(max_length=200)
    feature_category: int = IntegerChoicesField(choices_enum=FeatureCategoryEnum, default="None")  # type: ignore[reportAssignmentType]
    description = models.TextField(null=True)
    cash_RTM_code = models.CharField(null=True, max_length=40)

    @typing.override
    def __str__(self):
        return f"{self.feature_category} - {self.name}"


class Sector(models.Model):
    """Model representing tool sector."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    sector_owners = models.ManyToManyField(User, related_name="sector_owners", blank=True)

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
    order = models.PositiveIntegerField[int, int]()

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
    order = models.PositiveIntegerField[int, int]()

    class Meta(UserResource.Meta):
        ordering = ["question", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_question_order",
            ),
        ]

    @typing.override
    def __str__(self):
        return f"{self.question.title} - {self.text}"


class Tool(UserResource):
    """Model representing tool."""

    catalogs = models.ManyToManyField(
        Catalog,
        related_name="tool_catalogs",
        help_text="After adding or updating a catalog, the related questions are automatically populated to this tool.",
    )
    name = models.CharField[str, str](max_length=200)
    tagline = models.CharField[str, str](max_length=300, blank=True)
    description = models.TextField[str, str]()
    video_link = models.URLField[str, str](blank=True, null=True, validators=[validate_url])
    tool_link = models.CharField[str, str](blank=True, null=True)
    logo = models.ImageField(
        upload_to="logos/",
        verbose_name="Logo",
        null=True,
        blank=True,
    )
    tool_sectors = models.ManyToManyField(Sector, related_name="tool_sectors", blank=True)
    tool_features = models.ManyToManyField(ToolFeature, related_name="tool_features", blank=True)
    tool_owners = models.ManyToManyField(User, related_name="tool_owners", blank=True)

    class Meta(UserResource.Meta):
        ordering = ["name"]

    @typing.override
    def __str__(self):
        return f"{self.name}"


class OrdinalTypeEnum(models.IntegerChoices):
    """Enum representing scale of ordinal type question."""

    """
        Note: The enum labels are intentionally descriptive and user-friendly so they can be
        used directly in the frontend UI and remain consistent with design requirements.
    """
    NOT_AVAILABLE = (
        100,
        ("We don't know enough to answer at this time or don't want to include this when considering options"),
    )
    ONE = 1, ("One")
    TWO = 2, ("Two")
    THREE = 3, ("Three")
    FOUR = 4, ("Four")


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

    # typing
    question_id: typing.ClassVar[int]
    ordinal_value: int | None

    class Meta(UserResource.Meta):
        verbose_name = "Tool Answer"
        verbose_name_plural = "Tool Answers"
        constraints = [
            models.UniqueConstraint(
                fields=["tool", "question"],
                name="unique_tool_question",
            ),
        ]

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

    # typing
    question_id: typing.ClassVar[int]

    class Meta(UserResource.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "question"],
                name="unique_submission_question",
            ),
        ]
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
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "rank"],
                name="unique_submission_rank",
            ),
        ]
        ordering = ["submission", "rank"]
        verbose_name = "Recommendation Result"
        verbose_name_plural = "Recommendation Results"

    @typing.override
    def __str__(self):
        return f"#{self.rank} {self.tool.name} (score: {self.score:.2f})"
