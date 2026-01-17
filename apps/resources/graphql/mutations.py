import strawberry
import strawberry_django
from strawberry_django.permissions import IsAuthenticated

from apps.resources.graphql.inputs import ContactRequestInput
from apps.resources.graphql.types import ContactRequestType
from apps.resources.serializers import ContactRequestSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_contact_request(
        self,
        info: Info,
        data: ContactRequestInput,
    ) -> MutationResponseType[ContactRequestType]:
        return await ModelMutation(ContactRequestSerializer).handle_create_mutation(data, info, None)
