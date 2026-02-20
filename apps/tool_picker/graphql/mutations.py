import strawberry
import strawberry_django

from apps.tool_picker.graphql.inputs import UserSubmissionInput
from apps.tool_picker.graphql.types import UserSubmissionType
from apps.tool_picker.serializers import UserSubmissionSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    @strawberry_django.mutation
    async def create_user_submission(
        self,
        info: Info,
        data: UserSubmissionInput,
    ) -> MutationResponseType[UserSubmissionType]:
        return await ModelMutation(UserSubmissionSerializer).handle_create_mutation(
            data,
            info,
            None,
        )
