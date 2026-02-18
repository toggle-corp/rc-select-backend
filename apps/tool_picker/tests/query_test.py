import typing

from apps.tool_picker.factories import (
    CatalogFactory,
    CheckboxOptionFactory,
    QuestionFactory,
    ToolAnswerFactory,
    ToolFactory,
)
from apps.tool_picker.models import OrdinalTypeEnum, QuestionTypeEnum
from apps.user.factories import UserFactory
from main.tests import TestCase


class TestToolQueries(TestCase):
    class Query:
        TOOLS = """
            query Tools($pagination: OffsetPaginationInput) {
            tools(order: {id: ASC},pagination: $pagination) {
                totalCount
                pageInfo {
                   offset
                   limit
                }
                results {
                id
                name
                description
                tagline
                toolLink
                videoLink
                logo {
                    name
                    size
                    url
                }
                catalogs {
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
                answers {
                    id
                    description
                    question {
                        id
                        title
                    }
                    toolId
                }
                }
            }
            }
        """

        CATALOGS = """
            query Catalogs($pagination: OffsetPaginationInput) {
              catalogs(order: {id: ASC},pagination: $pagination) {
                totalCount
                pageInfo {
                   offset
                   limit
                 }
                results {
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
                    options {
                      id
                      question{
                          id
                          title
                      }
                      text
                      order
                    }
                  }
                }
              }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = UserFactory.create(email="testuser@example.com")

        cls.catalog = CatalogFactory.create(
            created_by=cls.user,
            modified_by=cls.user,
        )

        cls.tool = ToolFactory.create(
            catalogs=[cls.catalog],
            created_by=cls.user,
            modified_by=cls.user,
        )

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
        cls.tool_answer = ToolAnswerFactory.create(
            tool=cls.tool,
            description="Test",
            question=cls.question,
            ordinal_value=OrdinalTypeEnum.ONE,
        )

    def test_catalogs_query(self):
        def _query():
            return self.query_check(
                self.Query.CATALOGS,
                variables={
                    "pagination": {
                        "limit": 10,
                        "offset": 0,
                    },
                },
            )

        content = _query()

        assert content["data"]["catalogs"] == {
            **self.g_pagination(
                offset=0,
                limit=10,
                total_count=1,
                results=[
                    dict(
                        id=self.gID(self.catalog.pk),
                        name=self.catalog.name,
                        description=self.catalog.description,
                        showInHelpMeChoose=self.catalog.show_in_help_me_choose,
                        questions=[
                            dict(
                                id=self.gID(self.question.pk),
                                catalogId=self.gID(self.catalog.pk),
                                title=self.question.title,
                                description=self.question.description,
                                order=self.question.order,
                                questionType=(self.question.get_question_type_display().upper()),
                                label1=self.question.label_1,
                                label2=self.question.label_2,
                                label3=self.question.label_3,
                                label4=self.question.label_4,
                                labelNa=self.question.label_na,
                                options=[
                                    dict(
                                        id=self.gID(self.options.pk),
                                        question=dict(
                                            id=self.gID(self.question.pk),
                                            title=self.question.title,
                                        ),
                                        text=self.options.text,
                                        order=self.options.order,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        }, content

    def test_tools_query(self):
        def _query():
            return self.query_check(
                self.Query.TOOLS,
                variables={
                    "pagination": {
                        "limit": 10,
                        "offset": 0,
                    },
                },
            )

        content = _query()

        assert content["data"]["tools"] == {
            **self.g_pagination(
                offset=0,
                limit=10,
                total_count=1,
                results=[
                    dict(
                        id=self.gID(self.tool.pk),
                        name=self.tool.name,
                        description=self.tool.description,
                        tagline=self.tool.tagline,
                        toolLink=self.tool.tool_link,
                        videoLink=self.tool.video_link,
                        logo=(
                            dict(
                                name=self.tool.logo.name,
                                size=self.tool.logo.size,
                                url=self.tool.logo.url,
                            )
                            if self.tool.logo
                            else None
                        ),
                        catalogs=[
                            dict(
                                id=self.gID(self.catalog.pk),
                                name=self.catalog.name,
                                description=self.catalog.description,
                                showInHelpMeChoose=self.catalog.show_in_help_me_choose,
                                questions=[
                                    dict(
                                        id=self.gID(self.question.pk),
                                        catalogId=self.gID(self.catalog.pk),
                                        title=self.question.title,
                                        description=self.question.description,
                                        order=self.question.order,
                                        questionType=(self.question.get_question_type_display().upper()),
                                        label1=self.question.label_1,
                                        label2=self.question.label_2,
                                        label3=self.question.label_3,
                                        label4=self.question.label_4,
                                        labelNa=self.question.label_na,
                                    ),
                                ],
                            ),
                        ],
                        answers=[
                            dict(
                                id=self.gID(self.tool_answer.pk),
                                description=self.tool_answer.description,
                                question=dict(
                                    id=self.gID(self.question.pk),
                                    title=self.question.title,
                                ),
                                toolId=self.gID(self.tool.pk),
                            ),
                        ],
                    ),
                ],
            ),
        }, content
