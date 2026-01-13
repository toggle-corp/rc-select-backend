import strawberry
import strawberry_django

from apps.tool_picker.models import Catalog, Tool


@strawberry_django.filters.filter(Catalog, lookups=True)
class CatalogFilter:
    id: strawberry.ID | None
    show_in_help_me_choose: strawberry.auto


@strawberry_django.filters.filter(Tool, lookups=True)
class ToolFilter:
    id: strawberry.ID | None
    catalog_id: strawberry.auto
