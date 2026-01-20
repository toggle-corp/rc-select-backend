import typing

from captcha.models import CaptchaStore

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
        # Generates CAPTCHA key and value
        captcha_key = CaptchaStore.generate_key()
        captcha_obj = CaptchaStore.objects.get(hashkey=captcha_key)
        captcha_code = captcha_obj.response

        contact_request_data = {
            "name": "John",
            "email": "john@test.com",
            "nationalSociety": "Test National Society",
            "content": "This is test content",
            "captchaHashkey": captcha_key,
            "captchaCode": captcha_code,
        }

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

    def test_create_contact_request_without_captcha(self):
        contact_request_data = {
            "name": "John",
            "email": "john@test.com",
            "nationalSociety": "Test National Society",
            "content": "This is test content",
            "captchaHashkey": "",
            "captchaCode": "",
        }

        content = self._create_contact_request_mutation(data=contact_request_data)
        response = content["data"]["createContactRequest"]

        assert response["ok"] is False
        assert response["result"] is None

        assert response["errors"] == [
            {
                "field": "captchaCode",
                "client_id": None,
                "messages": "This field may not be blank.",
                "object_errors": None,
                "array_errors": None,
                "pydantic_errors": None,
            },
            {
                "field": "captchaHashkey",
                "client_id": None,
                "messages": "This field may not be blank.",
                "object_errors": None,
                "array_errors": None,
                "pydantic_errors": None,
            },
        ]
