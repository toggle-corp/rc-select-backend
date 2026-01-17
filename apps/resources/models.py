import datetime
import typing

from django.db import models

from apps.common.models import UserResource
from apps.tool_picker.models import Tool


class ContactRequest(models.Model):
    """Model representing contact where anyone can react out to the admins."""

    name = models.CharField[str, str](max_length=200)
    email = models.CharField[str, str](max_length=200)
    created_at = models.DateTimeField[datetime.datetime, datetime.datetime](auto_now_add=True)
    national_society = models.CharField[str, str](max_length=200)
    content = models.TextField[str, str](blank=True, null=True)

    class Meta:
        ordering = ["name"]

    @typing.override
    def __str__(self):
        return self.name


class CaseStudy(UserResource):
    """Model representing case study of national society for specific tool."""

    title = models.CharField[str, str](max_length=200)
    content = models.TextField[str, str]()
    cover_image = models.ImageField(
        upload_to="case_studies/",
        verbose_name="Case Study Cover Image",
        null=True,
        blank=True,
    )
    tool = models.ForeignKey[Tool, Tool](
        Tool,
        on_delete=models.CASCADE,
        related_name="case_studies",
    )

    class Meta(UserResource.Meta):
        ordering = ["title"]

    @typing.override
    def __str__(self):
        return self.title
