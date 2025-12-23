import datetime
import typing

from django.db import models

if typing.TYPE_CHECKING:
    from apps.user.models import User  # noqa: F401, RUF100, TC004


# -- Abstracts
class UserResource(models.Model):
    """Abstract base model for resources created or modified by a user."""

    created_at = models.DateTimeField[datetime.datetime, datetime.datetime](auto_now_add=True)
    modified_at = models.DateTimeField[datetime.datetime, datetime.datetime](auto_now=True)
    created_by = models.ForeignKey["User", "User"](
        "user.User",
        related_name="%(class)s_created",
        on_delete=models.PROTECT,
    )
    modified_by = models.ForeignKey["User", "User"](
        "user.User",
        related_name="%(class)s_modified",
        on_delete=models.PROTECT,
    )

    # Typing
    id: typing.ClassVar[int]
    pk: int
    created_by_id: typing.ClassVar[int]
    modified_by_id: typing.ClassVar[int]

    class Meta:
        abstract = True
        ordering = ["-id"]

    @typing.override
    def __str__(self):
        return str(self.pk)
