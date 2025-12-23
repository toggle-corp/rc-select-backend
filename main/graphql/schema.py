import strawberry
from django.core.files.uploadedfile import UploadedFile
from strawberry.django.views import AsyncGraphQLView
from strawberry.file_uploads import Upload
from strawberry_django.optimizer import DjangoOptimizerExtension

from apps.tool_picker.graphql import queries as tool_picker_queries

from .context import GraphQLContext
from .dataloaders import GlobalDataLoader
from .enums import AppEnumCollection, AppEnumCollectionData


class CustomAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(self, *args, **kwargs) -> GraphQLContext:  # type: ignore[reportIncompatibleMethodOverride]
        return GraphQLContext(
            *args,
            **kwargs,
            dl=GlobalDataLoader(),
        )


@strawberry.type
class Query(
    tool_picker_queries.Query,
):
    enums: AppEnumCollection = strawberry.field(  # type: ignore[reportGeneralTypeIssues]
        resolver=lambda: AppEnumCollectionData(),
    )


# NOTE: for now we are not using mutation
# @strawberry.type
# class Mutation: ...


schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,
    ],
    scalar_overrides={
        UploadedFile: Upload,
    },
)
