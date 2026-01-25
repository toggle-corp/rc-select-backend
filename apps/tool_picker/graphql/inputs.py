import strawberry


@strawberry.input()
class UserAnswerInput:
    catalog: strawberry.ID
    question: strawberry.ID
    ordinal_value: int | None = strawberry.UNSET
