import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import CaseStudyFilter
from .orders import CaseStudyOrder
from .types import CaseStudyType


@strawberry.type
class Query:
    case_studies: OffsetPaginated[CaseStudyType] = strawberry_django.offset_paginated(
        order=CaseStudyOrder,
        filters=CaseStudyFilter,
    )

    case_study: CaseStudyType = strawberry_django.field()
