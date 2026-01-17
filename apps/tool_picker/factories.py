import factory
from factory.django import DjangoModelFactory
from apps.user.factories import UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Catalog, Tool

class CatalogFactory(DjangoModelFactory[Catalog]):
    class Meta:
        model = Catalog

    name = factory.Sequence(lambda n: f"Catalog {n}")
    description = factory.Faker("paragraph")
    show_in_help_me_choose = False

    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)


class ToolFactory(DjangoModelFactory[Tool]):
    class Meta:
        model = Tool

    catalog = factory.SubFactory(CatalogFactory)

    name = factory.Sequence(lambda n: f"Tool {n}")
    tagline = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph")

    video_link = factory.Faker("url")
    tool_link = factory.Faker("url")
    logo = SimpleUploadedFile(
        "logo.png",
        b"fake-image-content",
        content_type="image/png",
    )
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)
