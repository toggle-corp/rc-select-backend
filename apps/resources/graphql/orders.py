import strawberry
import strawberry_django

from apps.resources.models import CaseStudy


@strawberry_django.order_type(CaseStudy)
class CaseStudyOrder:
    id: strawberry.auto
