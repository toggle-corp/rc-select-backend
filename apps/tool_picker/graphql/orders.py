import strawberry
import strawberry_django

from apps.tool_picker.models import Catalog, RecommendationResult, Tool


@strawberry_django.order_type(Catalog)
class CatalogOrder:
    id: strawberry.auto


@strawberry_django.order_type(Tool)
class ToolOrder:
    id: strawberry.auto


@strawberry_django.order_type(RecommendationResult)
class RecommendationResultOrder:
    id: strawberry.auto
    rank: strawberry.auto
