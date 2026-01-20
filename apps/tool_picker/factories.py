from factory.declarations import SubFactory
from factory.django import DjangoModelFactory

from apps.tool_picker.models import Catalog, Tool
from apps.user.factories import UserFactory


class CatalogFactory(DjangoModelFactory[Catalog]):
    class Meta:  # type: ignore[misc]
        model = Catalog

    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)


class ToolFactory(DjangoModelFactory[Tool]):
    class Meta:  # type: ignore[misc]
        model = Tool

    catalog = SubFactory(CatalogFactory)
    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)
