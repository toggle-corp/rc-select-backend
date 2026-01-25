import strawberry
import strawberry_django

from apps.tool_picker.graphql.inputs import UserAnswerInput
from apps.tool_picker.graphql.types import UserAnswerType
from apps.tool_picker.serializers import UserAnswerSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType


@strawberry.type
class Mutation:
    @strawberry_django.mutation
    async def create_user_answer(
        self,
        info: Info,
        data: UserAnswerInput,
    ) -> MutationResponseType[UserAnswerType]:
        return await ModelMutation(UserAnswerSerializer).handle_create_mutation(
            data,
            info,
            None,
        )
