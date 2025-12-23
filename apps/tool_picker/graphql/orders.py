import strawberry
import strawberry_django

from apps.tool_picker.models import Catalog, Tool


@strawberry_django.ordering.order(Catalog)
class CatalogOrder:
    id: strawberry.auto


@strawberry_django.ordering.order(Tool)
class ToolOrder:
    id: strawberry.auto
