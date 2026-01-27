import strawberry
import strawberry_django

from apps.tool_picker.models import UserAnswer


@strawberry_django.input(UserAnswer)
class UserAnswerInput:
    catalog: strawberry.ID
    question: strawberry.ID
    ordinal_value: int | None = strawberry.UNSET
    selected_options: list[strawberry.ID] | None = strawberry.UNSET
