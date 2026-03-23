import typing

from apps.tool_picker.factories import (
    CatalogFactory,
    CheckboxOptionFactory,
    QuestionFactory,
    ToolAnswerFactory,
    ToolFactory,
    UserAnswerFactory,
)
from apps.tool_picker.models import (
    OrdinalTypeEnum,
    QuestionTypeEnum,
    RecommendationResult,
    UserSubmission,
)
from apps.tool_picker.utils import calculate_recommendations
from main.tests import TestCase


class CalculateRecommendationsTest(TestCase):
    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Catalog
        cls.catalog = CatalogFactory()

        cls.ordinal_question = QuestionFactory(
            catalog=cls.catalog,
            question_type=QuestionTypeEnum.ORDINAL,
        )

        cls.checkbox_question = QuestionFactory(
            catalog=cls.catalog,
            question_type=QuestionTypeEnum.CHECKBOX,
        )

        cls.checkbox_option1 = CheckboxOptionFactory(question=cls.checkbox_question)
        cls.checkbox_option2 = CheckboxOptionFactory(question=cls.checkbox_question)

        # Submission
        cls.submission = UserSubmission.objects.create(
            catalog=cls.catalog,
        )

        # User ordinal answer = 2

        UserAnswerFactory.create(
            submission=cls.submission,
            question=cls.ordinal_question,
            ordinal_value=OrdinalTypeEnum.TWO,
        )

        # User checkbox answer selects
        user_answer = UserAnswerFactory.create(
            submission=cls.submission,
            question=cls.checkbox_question,
        )
        user_answer.selected_options.add(cls.checkbox_option1)

        # -------- Tool 1 (best match) --------
        cls.tool1 = ToolFactory(catalogs=[cls.catalog])

        ToolAnswerFactory(
            tool=cls.tool1,
            question=cls.ordinal_question,
            ordinal_value=OrdinalTypeEnum.ONE,
        )

        tool1_with_checkbox = ToolAnswerFactory(
            tool=cls.tool1,
            question=cls.checkbox_question,
        )
        tool1_with_checkbox.selected_options.add(cls.checkbox_option1)

        # -------- Tool 2 (worse match) --------
        cls.tool2 = ToolFactory(catalogs=[cls.catalog])

        ToolAnswerFactory(
            tool=cls.tool2,
            question=cls.ordinal_question,
            ordinal_value=OrdinalTypeEnum.FOUR,
        )

        t2__with_checkbox = ToolAnswerFactory(
            tool=cls.tool2,
            question=cls.checkbox_question,
        )
        t2__with_checkbox.selected_options.add(cls.checkbox_option1)

    def test_calculate_recommendations(cls):
        calculate_recommendations(cls.submission)

        results = RecommendationResult.objects.filter(
            submission=cls.submission,
        ).order_by("rank")

        assert results[0].tool == cls.tool1
        assert results[0].rank == 1
        assert results[0].score == 2  # tool1

        assert results[1].tool == cls.tool2
        assert results[1].rank == 2
        assert results[1].score == 1  # tool2
