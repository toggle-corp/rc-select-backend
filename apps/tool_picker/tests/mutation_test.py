import typing

from apps.tool_picker.factories import (
    CatalogFactory,
    CheckboxOptionFactory,
    QuestionFactory,
    ToolAnswerFactory,
    ToolFactory,
)
from apps.tool_picker.models import (
    OrdinalTypeEnum,
    QuestionTypeEnum,
    UserAnswer,
    UserSubmission,
)
from main.tests import TestCase


class TestToolMutation(TestCase):
    class Mutation:
        CREATE_USER_SUBMISSION = """
            mutation CreateUserSubmission($data: UserSubmissionInput!) {
                createUserSubmission(data: $data) {
                    ... on UserSubmissionTypeMutationResponseType {
                        errors
                        ok
                        result {
                            id
                            catalogId
                        }
                    }
                    ... on OperationInfo {
                        __typename
                        messages {
                            code
                            field
                            kind
                            message
                        }
                    }
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.catalog1 = CatalogFactory.create()
        cls.catalog2 = CatalogFactory.create()
        cls.catalog3 = CatalogFactory.create()
        # ORDINAL question
        cls.ordinal_question = QuestionFactory.create(
            catalog=cls.catalog1,
            question_type=QuestionTypeEnum.ORDINAL,
        )
        cls.ordinal_question2 = QuestionFactory.create(
            catalog=cls.catalog3,
            question_type=QuestionTypeEnum.ORDINAL,
        )

        # CHECKBOX question
        cls.checkbox_question = QuestionFactory.create(
            catalog=cls.catalog2,
            question_type=QuestionTypeEnum.CHECKBOX,
        )
        cls.checkbox_question2 = QuestionFactory.create(
            catalog=cls.catalog3,
            question_type=QuestionTypeEnum.CHECKBOX,
        )

        cls.checkbox_option1 = CheckboxOptionFactory.create(
            question=cls.checkbox_question,
        )
        cls.checkbox_option2 = CheckboxOptionFactory.create(
            question=cls.checkbox_question,
        )
        cls.checkbox_option3 = CheckboxOptionFactory.create(
            question=cls.checkbox_question2,
        )
        cls.checkbox_option4 = CheckboxOptionFactory.create(
            question=cls.checkbox_question2,
        )

        cls.tool = ToolFactory.create(
            catalogs=[cls.catalog2, cls.catalog1],
            name="Tool A",
        )

        cls.tool_answer = ToolAnswerFactory.create(
            tool=cls.tool,
            question=cls.ordinal_question,
            ordinal_value=OrdinalTypeEnum.FOUR.value,
            description="Test answer",
        )

    def _create_user_submission_mutation(self, data: dict[str, typing.Any]):
        return self.query_check(
            query=self.Mutation.CREATE_USER_SUBMISSION,
            variables={"data": data},
        )

    def test_create_submission_with_ordinal_answer(self):
        data = {
            "catalog": self.catalog1.pk,
            "answers": [
                {
                    "question": self.ordinal_question.pk,
                    "ordinalValue": OrdinalTypeEnum.ONE.value,
                },
            ],
        }

        content = self._create_user_submission_mutation(data)
        response_data = content["data"]["createUserSubmission"]

        assert response_data["ok"] is True
        assert response_data["errors"] is None

        submission = UserSubmission.objects.get(pk=response_data["result"]["id"])
        answer = UserAnswer.objects.get(submission=submission)
        assert answer.question == self.ordinal_question
        assert answer.ordinal_value == OrdinalTypeEnum.ONE.value
        assert answer.selected_options.count() == 0

    def test_create_submission_with_same_catalog(self):
        data = {
            "catalog": self.catalog3.pk,
            "answers": [
                {
                    "question": self.ordinal_question2.pk,
                    "ordinalValue": OrdinalTypeEnum.ONE.value,
                },
                {
                    "question": self.checkbox_question2.pk,
                    "selectedOptions": [
                        self.checkbox_option3.pk,
                        self.checkbox_option4.pk,
                    ],
                },
            ],
        }

        content = self._create_user_submission_mutation(data)
        response_data = content["data"]["createUserSubmission"]

        assert response_data["ok"] is True
        assert response_data["errors"] is None

        submission = UserSubmission.objects.get(pk=response_data["result"]["id"])

        ordinal_answer = UserAnswer.objects.get(
            submission=submission,
            question=self.ordinal_question2,
        )
        checkbox_answer = UserAnswer.objects.get(
            submission=submission,
            question=self.checkbox_question2,
        )
        selected_ids = set(
            checkbox_answer.selected_options.values_list("id", flat=True),
        )
        assert selected_ids == {
            self.checkbox_option3.id,
            self.checkbox_option4.id,
        }

        assert ordinal_answer.ordinal_value == OrdinalTypeEnum.ONE.value
        assert ordinal_answer.selected_options.count() == 0

    def test_create_submission_with_checkbox_answers(self):
        data = {
            "catalog": self.catalog2.pk,
            "answers": [
                {
                    "question": self.checkbox_question.pk,
                    "selectedOptions": [
                        self.checkbox_option1.pk,
                        self.checkbox_option2.pk,
                    ],
                },
            ],
        }

        content = self._create_user_submission_mutation(data)
        response_data = content["data"]["createUserSubmission"]

        assert response_data["ok"] is True
        assert response_data["errors"] is None

        submission = UserSubmission.objects.get(pk=response_data["result"]["id"])
        answer = UserAnswer.objects.get(submission=submission)
        assert answer.question == self.checkbox_question
        selected_ids = set(
            answer.selected_options.values_list("id", flat=True),
        )
        assert selected_ids == {
            self.checkbox_option1.id,
            self.checkbox_option2.id,
        }

    def test_ordinal_question_with_selected_options(self):
        data = {
            "catalog": self.catalog1.pk,
            "answers": [
                {
                    "question": self.ordinal_question.pk,
                    "selectedOptions": [
                        self.checkbox_option1.pk,
                    ],
                },
            ],
        }

        content = self._create_user_submission_mutation(data)
        response_data = content["data"]["createUserSubmission"]

        assert response_data["errors"] == [
            {
                "array_errors": [
                    {
                        "client_id": "NOT_FOUND_0",
                        "messages": None,
                        "object_errors": [
                            {
                                "array_errors": None,
                                "client_id": None,
                                "field": "ordinalValue",
                                "messages": (
                                    f"Selected question is {self.ordinal_question.get_question_type_display()} "
                                    "type question and requires an ordinal value."
                                ),
                                "object_errors": None,
                                "pydantic_errors": None,
                            },
                        ],
                    },
                ],
                "client_id": None,
                "field": "answers",
                "messages": None,
                "object_errors": None,
                "pydantic_errors": None,
            },
        ], content

    def test_checkbox_question_with_ordinal_value(self):
        data = {
            "catalog": self.catalog1.pk,
            "answers": [
                {
                    "question": self.checkbox_question.pk,
                    "ordinalValue": OrdinalTypeEnum.FOUR.value,
                },
            ],
        }

        content = self._create_user_submission_mutation(data)
        response_data = content["data"]["createUserSubmission"]

        assert response_data["errors"] == [
            {
                "array_errors": [
                    {
                        "client_id": "NOT_FOUND_0",
                        "messages": None,
                        "object_errors": [
                            {
                                "array_errors": None,
                                "client_id": None,
                                "field": "ordinalValue",
                                "messages": (
                                    f"Selected question is {self.checkbox_question.get_question_type_display()} "
                                    "and should not have an ordinal value."
                                ),
                                "object_errors": None,
                                "pydantic_errors": None,
                            },
                        ],
                    },
                ],
                "client_id": None,
                "field": "answers",
                "messages": None,
                "object_errors": None,
                "pydantic_errors": None,
            },
        ], content
