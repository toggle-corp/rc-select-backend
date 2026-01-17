# pyright: reportRedeclaration=false
# pyright: reportIncompatibleVariableOverride=false
# pyright: reportMissingTypeArgument=false
import typing

from factory.declarations import SubFactory
from factory.django import DjangoModelFactory

from apps.tool_picker.models import Catalog, Tool
from apps.user.factories import UserFactory


class CatalogFactory(DjangoModelFactory):
    class Meta:
        model: type[Catalog] = Catalog

    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)


class ToolFactory(DjangoModelFactory):
    class Meta:
        model: type[Tool] = Tool

    catalog = SubFactory(CatalogFactory)
    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)


if typing.TYPE_CHECKING:
    ToolFactory: type[DjangoModelFactory[Tool]]
    CatalogFactory: type[DjangoModelFactory[Catalog]]
