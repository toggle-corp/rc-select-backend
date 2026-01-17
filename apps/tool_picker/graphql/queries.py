import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import CatalogFilter, ToolFilter
from .orders import CatalogOrder, ToolOrder
from .types import CatalogType, ToolType


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
