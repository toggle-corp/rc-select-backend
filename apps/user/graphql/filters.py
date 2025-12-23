import strawberry
import strawberry_django
from django.db import models

from apps.user.models import User


@strawberry_django.filters.filter(User, lookups=True)
class UserFilter:
    id: strawberry.auto

    @strawberry_django.filter_field
    def search(
        self,
        queryset: models.QuerySet[User],
        value: str,
        prefix: str,
    ) -> tuple[models.QuerySet[User], models.Q]:
        return queryset, models.Q(
            **{
                f"{prefix}display_name__icontains": value,
            },
        )
