import strawberry
import strawberry_django

from apps.resources.models import CaseStudy, ContactRequest
from apps.tool_picker.graphql.filters import ToolFilter


@strawberry_django.filters.filter(ContactRequest, lookups=True)
class ContactRequestFilter:
    id: strawberry.ID | None = strawberry.UNSET


@strawberry_django.filters.filter(CaseStudy, lookups=True)
class CaseStudyFilter:
    id: strawberry.ID | None = strawberry.UNSET
    tool: ToolFilter | None = strawberry.UNSET
