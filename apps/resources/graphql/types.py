import strawberry
import strawberry_django

from apps.resources.models import CaseStudy, ContactRequest
from utils.graphql.types import DjangoFileType


@strawberry_django.type(CaseStudy)
class CaseStudyType:
    id: strawberry.ID
    title: strawberry.auto
    tool_id: strawberry.ID
    content: strawberry.auto
    cover_image: DjangoFileType | None
    link: strawberry.auto


@strawberry_django.type(ContactRequest)
class ContactRequestType:
    id: strawberry.ID
    name: strawberry.auto
    email: strawberry.auto
    created_at: strawberry.auto
    content: strawberry.auto
    national_society: strawberry.auto
