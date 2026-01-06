# pyright: reportUninitializedInstanceVariable=false
import typing

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class User(AbstractUser):
    """Custom user model with email as unique identifier."""

    EMAIL_FIELD = USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username = None
    email = models.EmailField[str, str](unique=True)
    display_name = models.CharField[str, str](max_length=255)

    objects: CustomUserManager = CustomUserManager()  # type: ignore[reportAssignmentType]

    # type hints
    pk: int

    @property
    def anonymized_email(self):
        email_name, email_domain = self.email.split("@")
        email_name_first_char, email_name_last_char = email_name[:1], email_name[-1:]
        return f"{email_name_first_char}***{email_name_last_char}@{email_domain}"

    @typing.override
    def save(self, *args, **kwargs):  # type: ignore[reportMissingParameterType]
        # Make sure email are same and lowercase
        self.email = self.email.lower()
        if self.pk is None:  # type: ignore[reportUnnecessaryComparison]
            super().save(*args, **kwargs)
            # Remove force_insert since we have already inserted
            kwargs.pop("force_insert", None)
        self.display_name = self.get_full_name() or f"User#{self.pk}"
        return super().save(*args, **kwargs)
