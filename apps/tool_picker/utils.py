"""Note:
Currently, the recommendation calculation only uses ordinal-type questions.
Checkbox or other question types are ignored, but support for these may be added in the future.
The algorithm compares user ordinal answers with tool answers, computes scores based on the differences
and ranks the tools accordingly.
"""

from django.db.models import Prefetch

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


def calculate_recommendations(submission: UserSubmission):
    """Calculate and assign the best matching tool for a given user submission
    based on the ordinal answers from the user and the tools corresponding answers.
    """
    user_answers = dict(
        submission.answers.filter(
            question__question_type=QuestionTypeEnum.ORDINAL,
            ordinal_value__isnull=False,
        )
        .exclude(ordinal_value=OrdinalTypeEnum.NOT_AVAILABLE)
        .values_list("question_id", "ordinal_value"),
    )

    if not user_answers:
        return

    tools = Tool.objects.filter(
        catalog=submission.catalog,
    ).prefetch_related(
        Prefetch(
            "answers",
            queryset=ToolAnswer.objects.filter(ordinal_value__isnull=False)
            .exclude(ordinal_value=OrdinalTypeEnum.NOT_AVAILABLE.value)
            .select_related("question"),
        ),
    )
    tool_scores = []

    for tool in tools:
        total_point = 0

        for tool_answer in tool.answers.all():
            if tool_answer.question_id not in user_answers:
                continue

            user_value = user_answers.get(tool_answer.question_id)
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
