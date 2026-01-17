import strawberry
import strawberry_django

from apps.resources.models import ContactRequest


@strawberry_django.input(ContactRequest)
class ContactRequestInput:
    name: strawberry.auto
    email: strawberry.auto
    national_society: strawberry.auto
    content: strawberry.auto
