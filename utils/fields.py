# from uuid import uuid4

from django.core.exceptions import ValidationError

# from django.db.models.fields.files import FileField, ImageField
from django.utils.translation import gettext


def validate_percentage(value: int):
    if not (0 <= value <= 100):
        raise ValidationError(
            gettext("The value %(value)s is not a valid percentage. It should be between 0 and 100."),
            params={"value": value},
        )


# class SecureFileField(FileField):
#     def generate_filename(self, instance, filename):
#         """Overwrites https://github.com/django/django/blob/main/django/db/models/fields/files.py#L345"""
#         # Append uuid4 path to the filename
#         filename = f"{uuid4().hex}/{filename}"
#         return super().generate_filename(instance, filename)


# class SecureImageField(ImageField):
#     def generate_filename(self, instance, filename):
#         filename = f"{uuid4().hex}/{filename}"
#         return super().generate_filename(instance, filename)
