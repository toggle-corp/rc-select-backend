import strawberry
import strawberry_django

from apps.resources.models import CaseStudy, ContactRequest


@strawberry_django.ordering.order(CaseStudy)
class CaseStudyOrder:
    id: strawberry.auto


@strawberry_django.ordering.order(ContactRequest)
class ContactRequestOrder:
    id: strawberry.auto
