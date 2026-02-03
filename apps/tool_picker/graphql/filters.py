import strawberry
import strawberry_django

from apps.tool_picker.models import Catalog, RecommendationResult, Tool, UserSubmission


@strawberry_django.filters.filter(Catalog, lookups=True)
class CatalogFilter:
    id: strawberry.ID | None
    show_in_help_me_choose: bool | None


@strawberry_django.filters.filter(Tool, lookups=True)
class ToolFilter:
    id: strawberry.ID | None
    catalog_id: strawberry.auto


@strawberry_django.filters.filter(UserSubmission, lookups=True)
class UserSubmissionFilter:
    id: strawberry.ID | None = strawberry.UNSET


@strawberry_django.filters.filter(RecommendationResult, lookups=True)
class RecommendationResultFilter:
    id: strawberry.ID | None = strawberry.UNSET
    submission: UserSubmissionFilter | None = strawberry.UNSET
