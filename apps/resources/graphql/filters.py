import strawberry
import strawberry_django

from apps.resources.models import ContactRequest, CaseStudy


@strawberry_django.filters.filter(ContactRequest, lookups=True)
class ContactRequestFilter:
    id: strawberry.ID | None


@strawberry_django.filters.filter(CaseStudy, lookups=True)
class CaseStudyFilter:
    id: strawberry.ID | None
