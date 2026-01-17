import typing

from apps.resources.models import ContactRequest
from apps.user.factories import UserFactory
from main.tests import TestCase


class TestContactRequestMutation(TestCase):
    class Mutation:
        CREATE_CONTACT_REQUEST = """
            mutation CreateContactRequest($data: ContactRequestInput!) {
            createContactRequest(data: $data) {
                ... on ContactRequestTypeMutationResponseType {
                errors
                ok
                result {
                    id
                    name
                    email
                    nationalSociety
                    content
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
        cls.user = UserFactory.create(email="test@gmail.com")

    def _create_contact_request_mutation(self, data: dict[str, str], **kwargs: typing.Any):
        return self.query_check(
            query=self.Mutation.CREATE_CONTACT_REQUEST,
            variables={
                "data": data,
            },
        )

    def test_create_contact_request(self):
        contact_request_data = {
            "name": "John",
            "email": "john@test.com",
            "nationalSociety": "Test National Society",
            "content": "This is test content",
        }

        # Without authentication
        content = self._create_contact_request_mutation(contact_request_data)

        assert content["data"]["createContactRequest"]["messages"] == [
            {
                "code": None,
                "field": "createContactRequest",
                "kind": "PERMISSION",
                "message": "User is not authenticated.",
            },
        ]

        # With authentication
        self.force_login(self.user)
        content = self._create_contact_request_mutation(data=contact_request_data)
        response_data = content["data"]["createContactRequest"]

        assert response_data["ok"] is True
        assert response_data["errors"] is None

        contact_request = ContactRequest.objects.get(pk=response_data["result"]["id"])
        assert response_data["result"] == {
            "id": self.gID(contact_request.pk),
            "name": contact_request.name,
            "email": contact_request.email,
            "content": contact_request.content,
            "nationalSociety": contact_request.national_society,
        }
