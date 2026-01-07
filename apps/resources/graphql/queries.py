import strawberry
import strawberry_django
from django.db.models import QuerySet
from strawberry_django.pagination import OffsetPaginated

from apps.resources.models import CaseStudy, ContactRequest

from .filters import CaseStudyFilter, ContactRequestFilter
from .orders import CaseStudyOrder, ContactRequestOrder
from .types import CaseStudyType, ContactRequestType


@strawberry.type
class Query:
    @strawberry_django.offset_paginated(
        OffsetPaginated[CaseStudyType],
        order=CaseStudyOrder,
        filters=CaseStudyFilter,
    )
    def caseStudies(
        self,
    ) -> QuerySet[CaseStudy]:
        return CaseStudy.objects.all()

    caseStudy: CaseStudyType = strawberry_django.field()

    @strawberry_django.offset_paginated(
        OffsetPaginated[ContactRequestType],
        order=ContactRequestOrder,
        filters=ContactRequestFilter,
    )
    def contactRequests(
        self,
    ) -> QuerySet[ContactRequest]:
        return ContactRequest.objects.all()

    contactRequest: ContactRequestType = strawberry_django.field()
