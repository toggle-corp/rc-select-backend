import strawberry


@strawberry.input
class UserAnswerInput:
    question: strawberry.ID
    ordinal_value: int | None = strawberry.UNSET
    selected_options: list[strawberry.ID] | None = strawberry.UNSET


@strawberry.input
class UserSubmissionInput:
    catalog: strawberry.ID
    answers: list[UserAnswerInput]
