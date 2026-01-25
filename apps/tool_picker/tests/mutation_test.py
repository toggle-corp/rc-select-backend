import typing

from apps.tool_picker.factories import (
    CatalogFactory,
    CheckboxOptionFactory,
    QuestionFactory,
)
from apps.tool_picker.models import OrdinalTypeEnum, QuestionTypeEnum, UserAnswer
from apps.user.factories import UserFactory
from main.tests import TestCase


class TestToolMutation(TestCase):
    class Mutation:
        CREATE_USER_ANSWER = """
            mutation CreateUserAnswer($data: UserAnswerInput!) {
                createUserAnswer(data: $data) {
                    ... on UserAnswerTypeMutationResponseType {
                        errors
                        ok
                        result {
                            id
                            catalog {
                                id
                                name
                                description
                                showInHelpMeChoose
                                questions {
                                    id
                                    catalogId
                                    title
                                    description
                                    order
                                    questionType
                                    label1
                                    label2
                                    label3
                                    label4
                                    labelNa
                                }
                            }
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
        cls.user = UserFactory.create(email="user@test.com")

        cls.catalog = CatalogFactory.create(created_by=cls.user, modified_by=cls.user)

        cls.question = QuestionFactory.create(
            catalog=cls.catalog,
            created_by=cls.user,
            modified_by=cls.user,
            question_type=QuestionTypeEnum.ORDINAL,
        )
        cls.options = CheckboxOptionFactory.create(
            question=cls.question,
            created_by=cls.user,
            modified_by=cls.user,
        )

    def _create_user_answer_mutation(self, data: dict[str, typing.Any]):
        return self.query_check(
            query=self.Mutation.CREATE_USER_ANSWER,
            variables={"data": data},
        )

    def test_create_user_answer(self):
        data = {
            "catalog": self.gID(self.catalog.pk),
            "question": self.gID(self.question.pk),
            "ordinalValue": OrdinalTypeEnum.ONE.value,
        }

        content = self._create_user_answer_mutation(data=data)
        response_data = content["data"]["createUserAnswer"]

        assert response_data["ok"] is True
        assert response_data["errors"] is None

        user_answer = UserAnswer.objects.get(pk=response_data["result"]["id"])
        assert response_data["result"] == {
            "id": self.gID(user_answer.pk),
            "catalog": {
                "id": self.gID(self.catalog.pk),
                "name": self.catalog.name,
                "description": self.catalog.description,
                "showInHelpMeChoose": self.catalog.show_in_help_me_choose,
                "questions": [
                    {
                        "id": self.gID(self.question.pk),
                        "catalogId": self.gID(self.catalog.pk),
                        "title": self.question.title,
                        "description": self.question.description,
                        "order": self.question.order,
                        "questionType": (self.question.get_question_type_display().upper()),
                        "label1": self.question.label_1,
                        "label2": self.question.label_2,
                        "label3": self.question.label_3,
                        "label4": self.question.label_4,
                        "labelNa": self.question.label_na,
                    },
                ],
            },
        }
