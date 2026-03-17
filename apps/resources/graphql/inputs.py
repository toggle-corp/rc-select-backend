import strawberry
import strawberry_django

from apps.resources.models import RequestDemo


@strawberry.input
class ContactRequestInput:
    name: str
    email: str
    national_society: str
    content: str
    captcha_hashkey: str
    captcha_code: str


@strawberry_django.input(RequestDemo)
class RequestDemoInput:
    name: strawberry.auto
    email: strawberry.auto
    content: strawberry.auto
    national_society: strawberry.auto
    tool: int
