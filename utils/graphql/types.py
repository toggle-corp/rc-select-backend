import typing

import strawberry
import strawberry_django
from django.core.files.storage import FileSystemStorage, default_storage
from django.db.models.fields import files
from django.db.models.fields.files import FileField, ImageField
from strawberry.types import Info
from strawberry_django.fields.types import field_type_map

ResultTypeVar = typing.TypeVar("ResultTypeVar")

# generalize all the CustomErrorType
CustomErrorType = strawberry.scalar(
    typing.NewType("CustomErrorType", object),
    description="A generic type to return error messages",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


@strawberry.type
class MutationResponseType(typing.Generic[ResultTypeVar]):
    ok: bool = True
    errors: CustomErrorType | None = None
    result: ResultTypeVar | None = None


# Replaces strawberry_django.fields.types.DjangoFileType
@strawberry.type
class DjangoFileType:
    name: str
    size: int

    @strawberry_django.field
    def url(
        self,
        info: Info,
        file: strawberry.Parent[files.FieldFile],
    ) -> str:
        if isinstance(default_storage, FileSystemStorage):
            return info.context.request.build_absolute_uri(file.url)
        return file.url


field_type_map.update(
    {
        FileField: DjangoFileType,
        ImageField: DjangoFileType,
    },
)
