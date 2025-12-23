import strawberry
import strawberry_django

from apps.tool_picker.models import (
    Catalog,
    CheckboxOption,
    Question,
    Tool,
    ToolAnswer,
)
from utils.graphql.types import DjangoFileType


@strawberry_django.type(CheckboxOption)
class CheckboxOptionType:
    id: strawberry.ID
    question_id: strawberry.ID
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
    description: strawberry.auto
    questions: list[QuestionType]


@strawberry_django.type(ToolAnswer)
class ToolAnswerType:
    id: strawberry.ID
    tool_id: strawberry.ID
    question_id: strawberry.ID
    description: strawberry.auto
    ordinal_value: strawberry.auto
    selected_options: list[CheckboxOptionType]


@strawberry_django.type(Tool)
class ToolType:
    id: strawberry.ID
    catalog: CatalogType
    name: strawberry.auto
    tagline: strawberry.auto
    description: strawberry.auto
    video_link: strawberry.auto
    tool_link: strawberry.auto
    logo: DjangoFileType | None
    answers: list[ToolAnswerType]
