"""Note: Recommendation scores tools based on user answers:
- Ordinal questions: score calculated from difference between tool answer and user answer
- Checkbox questions: tool must match at least one user-selected option, otherwise excluded.
Tools are ranked by total score and top 5 are saved for the submission.
"""

from django.db.models import Prefetch, Q

from apps.tool_picker.models import OrdinalTypeEnum, QuestionTypeEnum, RecommendationResult, Tool, ToolAnswer, UserSubmission


def calculate_score_from_diff(diff: int) -> int:
    """Convert difference between tool and user values to points.

    Scoring table:
    - diff = +3: -5 points (tool way more complex than user wants)
    - diff = +2: -3 points (tool more complex than user wants)
    - diff = +1: -1 points (tool slightly more complex)
    - diff = 0:  +1 point  (exact match)
    - diff < 0:  +3 points (tool simpler than user required)
    """
    if diff >= 3:
        return -5
    if diff == 2:
        return -3
    if diff == 1:
        return -1
    if diff == 0:
        return 1
    # diff < 0
    return 3


def is_checkbox_compatible(tool: Tool, user_checkbox_answers: dict[int, set[int]]) -> bool:
    for tool_answer in tool.answers.all():
        if tool_answer.question.question_type != QuestionTypeEnum.CHECKBOX:
            continue

        user_selected_options = user_checkbox_answers.get(tool_answer.question_id)

        if not user_selected_options:
            continue

        tool_supported_options = set(
            tool_answer.selected_options.values_list("id", flat=True),
        )

        # NOTE: If the tool answer does not share any options with the user answer, reject it
        if not (user_selected_options & tool_supported_options):
            return False
    return True


def calculate_recommendations(submission: UserSubmission):
    """Calculate and assign the best matching tool for a given user submission
    based on the ordinal answers from the user and the tools corresponding answers.
    """
    user_ordinal_answers = dict(
        submission.answers.filter(
            question__question_type=QuestionTypeEnum.ORDINAL,
            ordinal_value__isnull=False,
        )
        .exclude(ordinal_value=OrdinalTypeEnum.NOT_AVAILABLE)
        .values_list("question_id", "ordinal_value"),
    )

    checkbox_answers = submission.answers.filter(
        question__question_type=QuestionTypeEnum.CHECKBOX,
    ).prefetch_related("selected_options")

    user_checkbox_options = {
        ans.question_id: set(ans.selected_options.values_list("id", flat=True))
        for ans in checkbox_answers
        if ans.selected_options.exists()
    }

    tools = Tool.objects.filter(
        catalogs=submission.catalog,
    ).prefetch_related(
        Prefetch(
            "answers",
            queryset=ToolAnswer.objects.select_related("question")
            .prefetch_related("selected_options")
            .exclude(
                Q(question__question_type=QuestionTypeEnum.ORDINAL)
                & Q(ordinal_value__in=[None, OrdinalTypeEnum.NOT_AVAILABLE]),
            ),
        ),
    )
    tool_scores = []

    for tool in tools:
        # Skip tools that don't match user's checkbox selections
        if not is_checkbox_compatible(tool, user_checkbox_options):
            continue

        total_point = 0

        for tool_answer in tool.answers.all():
            if tool_answer.question_id not in user_ordinal_answers:
                continue

            user_value = user_ordinal_answers.get(tool_answer.question_id)
            if user_value is None:
                continue

            diff = tool_answer.ordinal_value - user_value
            total_point += calculate_score_from_diff(diff)

        tool_scores.append((tool, float(total_point)))

    sorted_tools = sorted(
        tool_scores,
        key=lambda x: x[1],
        reverse=True,
    )

    results = [
        RecommendationResult(
            submission=submission,
            tool=tool,
            rank=rank,
            score=score,
        )
        for rank, (tool, score) in enumerate(sorted_tools[:5], start=1)
    ]

    RecommendationResult.objects.bulk_create(results)
