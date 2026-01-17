import strawberry
import strawberry_django

<<<<<<< HEAD
from apps.resources.models import (
    CaseStudy,
    ContactRequest,
)
||||||| parent of e5fc916 (test(resources): add testcase for resource queries)
from apps.resources.models import (
    ContactRequest,
    CaseStudy,
)
=======
from apps.resources.models import CaseStudy, ContactRequest
>>>>>>> e5fc916 (test(resources): add testcase for resource queries)
from utils.graphql.types import DjangoFileType


@strawberry_django.type(CaseStudy)
class CaseStudyType:
    id: strawberry.ID
    title: strawberry.auto
    tool_id: strawberry.ID
    content: strawberry.auto
    cover_image: DjangoFileType | None


@strawberry_django.type(ContactRequest)
class ContactRequestType:
    id: strawberry.ID
    name: strawberry.auto
    email: strawberry.auto
    created_at: strawberry.auto
    content: strawberry.auto
    national_society: strawberry.auto
