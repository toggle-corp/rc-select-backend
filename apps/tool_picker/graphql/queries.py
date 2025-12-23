import strawberry
import strawberry_django
from django.db.models import QuerySet
from strawberry_django.pagination import OffsetPaginated

from apps.tool_picker.models import Catalog, Tool

from .filters import CatalogFilter, ToolFilter
from .orders import CatalogOrder, ToolOrder
from .types import CatalogType, ToolType


@strawberry.type
class Query:
    @strawberry_django.offset_paginated(
        OffsetPaginated[CatalogType],
        order=CatalogOrder,
        filters=CatalogFilter,
    )
    def catalogs(
        self,
    ) -> QuerySet[Catalog]:
        return Catalog.objects.all()

    catalog: CatalogType = strawberry_django.field()

    @strawberry_django.offset_paginated(
        OffsetPaginated[ToolType],
        order=ToolOrder,
        filters=ToolFilter,
    )
    def tools(
        self,
    ) -> QuerySet[Tool]:
        return Tool.objects.all()

    tool: ToolType = strawberry_django.field()
