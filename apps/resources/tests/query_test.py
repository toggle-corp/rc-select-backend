import typing

from apps.resources.factories import CaseStudyFactory
from apps.tool_picker.factories import ToolFactory
from apps.user.factories import UserFactory
from main.tests import TestCase


class TestResourceQueries(TestCase):
    class Query:
        CASE_STUDIES = """
            query CaseStudies($pagination: OffsetPaginationInput) {
              caseStudies(order: {id: ASC}, pagination: $pagination) {
                totalCount
                pageInfo {
                  offset
                  limit
                }
                results {
                  id
                  title
                  content
                  coverImage {
                    name
                  }
                }
              }
            }
        """

        CASE_STUDY = """
            query CaseStudy($id: ID!) {
              caseStudy(id: $id) {
                id
                title
                content
                coverImage {
                  name
                }
              }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.tool = ToolFactory.create()
        cls.case_studies = CaseStudyFactory.create_batch(
            3,
            tool=cls.tool,
            created_by=cls.user,
            modified_by=cls.user,
        )

    def test_case_studies(self):
        def _query():
            return self.query_check(
                self.Query.CASE_STUDIES,
                variables={
                    "pagination": {
                        "limit": 10,
                        "offset": 0,
                    },
                },
            )

        content = _query()

        assert content["data"]["caseStudies"] == {
            **self.g_pagination(
                offset=0,
                limit=10,
                total_count=len(self.case_studies),
                results=[
                    dict(
                        id=self.gID(case.pk),
                        title=case.title,
                        content=case.content,
                        coverImage=({"name": case.cover_image.name} if case.cover_image else None),
                    )
                    for case in self.case_studies
                ],
            ),
        }, content

    def test_case_study(self):
        case = self.case_studies[0]

        content = self.query_check(
            self.Query.CASE_STUDY,
            variables={"id": self.gID(case.pk)},
        )

        assert content["data"]["caseStudy"] == dict(
            id=self.gID(case.pk),
            title=case.title,
            content=case.content,
            coverImage=({"name": case.cover_image.name} if case.cover_image else None),
        ), content
