import strawberry
import strawberry_django

from apps.resources.graphql.inputs import ContactRequestInput, RequestDemoInput
from apps.resources.graphql.types import ContactRequestType, RequestDemoType
from apps.resources.serializers import ContactRequestSerializer, RequestDemoSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    @strawberry_django.mutation()
    async def create_contact_request(
        self,
        info: Info,
        data: ContactRequestInput,
    ) -> MutationResponseType[ContactRequestType]:
        return await ModelMutation(ContactRequestSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation()
    async def create_demo_request(
        self,
        info: Info,
        data: RequestDemoInput,
    ) -> MutationResponseType[RequestDemoType]:
        return await ModelMutation(RequestDemoSerializer).handle_create_mutation(data, info, None)
