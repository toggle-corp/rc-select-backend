import typing

from apps.user.factories import UserFactory
from main.tests import TestCase


class TestUserQuery(TestCase):
    class Query:
        ME = """
            query meQuery {
              me {
                email
                firstName
                lastName
                displayName
              }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(email="main-user@test.com")

    def test_me(self):
        # Without authentication -----
        content = self.query_check(self.Query.ME)
        assert content["data"]["me"] is None

        user = self.user
        # With authentication -----
        self.force_login(user)
        content = self.query_check(self.Query.ME)
        assert content["data"]["me"] == dict(
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            displayName=f"{user.first_name} {user.last_name}",
        )
