import strawberry
import strawberry_django

from apps.tool_picker.models import (
    Catalog,
    CheckboxOption,
    Question,
    RecommendationResult,
    Tool,
    ToolAnswer,
    UserAnswer,
)
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Question)
class QuestionTitleType:
    id: strawberry.ID
    title: strawberry.auto
    question_type: strawberry.auto
    description: strawberry.auto
    order: strawberry.auto


@strawberry_django.type(CheckboxOption)
class CheckboxOptionType:
    id: strawberry.ID
    question: QuestionTitleType
    order: strawberry.auto
    text: strawberry.auto


@strawberry_django.type(Question)
class QuestionType:
    id: strawberry.ID
    catalog_id: strawberry.ID
    question_type: strawberry.auto
    title: strawberry.auto
    description: strawberry.auto
    order: strawberry.auto
    label_na: strawberry.auto
    label_1: strawberry.auto
    label_2: strawberry.auto
    label_3: strawberry.auto
    label_4: strawberry.auto
    options: list[CheckboxOptionType]


@strawberry_django.type(Catalog)
class CatalogType:
    id: strawberry.ID
    name: strawberry.auto
    show_in_help_me_choose: strawberry.auto
    description: strawberry.auto
    questions: list[QuestionType]


@strawberry_django.type(ToolAnswer)
class ToolAnswerType:
    id: strawberry.ID
    tool_id: strawberry.ID
    question: QuestionTitleType
    description: strawberry.auto
    ordinal_value: int | None
    selected_options: list[CheckboxOptionType]


@strawberry_django.type(UserAnswer)
class UserAnswerType:
    question: QuestionTitleType
    ordinal_value: int | None
    selected_options: list[CheckboxOptionType]


@strawberry_django.type(Tool)
class ToolType:
    id: strawberry.ID
    catalogs: list[CatalogType]
    name: strawberry.auto
    tagline: strawberry.auto
    description: strawberry.auto
    video_link: strawberry.auto
    tool_link: strawberry.auto
    logo: DjangoFileType | None
    answers: list[ToolAnswerType]


@strawberry.type
class UserSubmissionType:
    id: strawberry.ID
    catalog_id: strawberry.ID
    answers: list[UserAnswerType]


@strawberry_django.type(RecommendationResult)
class RecommendationResultType:
    id: strawberry.auto
    submission: UserSubmissionType
    rank: strawberry.auto
    score: strawberry.auto
    tool: ToolType
