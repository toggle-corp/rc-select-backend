import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from rest_framework.exceptions import ValidationError

from apps.resources.graphql.inputs import ContactRequestInput
from apps.resources.graphql.types import ContactRequestType
from apps.resources.serializers import ContactRequestSerializer
from main.graphql.context import Info
from utils.common import validate_captcha
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import CustomErrorType, MutationResponseType


@strawberry.type
class Mutation:
    @strawberry_django.mutation()
    async def create_contact_request(
        self,
        info: Info,
        data: ContactRequestInput,
    ) -> MutationResponseType[ContactRequestType]:
        try:
            await sync_to_async(validate_captcha)(data.captcha_hashkey, data.captcha_code)
        except ValidationError as e:
            return MutationResponseType(
                ok=False,
                errors=CustomErrorType(
                    {
                        "code": None,
                        "field": "captch",
                        "kind": "VALIDATION",
                        "messages": str(e),
                    },
                ),
                result=None,
            )
        return await ModelMutation(ContactRequestSerializer).handle_create_mutation(
            data,
            info,
            None,
        )
