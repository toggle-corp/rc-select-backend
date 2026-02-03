import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import CatalogFilter, RecommendationResultFilter, ToolFilter
from .orders import CatalogOrder, RecommendationResultOrder, ToolOrder
from .types import CatalogType, RecommendationResultType, ToolType


@strawberry.type
class Query:
    catalogs: OffsetPaginated[CatalogType] = strawberry_django.offset_paginated(
        order=CatalogOrder,
        filters=CatalogFilter,
    )

    catalog: CatalogType = strawberry_django.field()

    tools: OffsetPaginated[ToolType] = strawberry_django.offset_paginated(
        order=ToolOrder,
        filters=ToolFilter,
    )

    tool: ToolType = strawberry_django.field()

    recommendation_results: OffsetPaginated[RecommendationResultType] = strawberry_django.offset_paginated(
        filters=RecommendationResultFilter,
        order=RecommendationResultOrder,
    )
    recommendation_result: RecommendationResultType = strawberry_django.field()
