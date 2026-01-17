import strawberry
import strawberry_django

from apps.user.models import User


@strawberry_django.order_type(User)
class UserOrder:
    id: strawberry.auto
