import factory
from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.tool_picker.models import (
    Catalog,
    CheckboxOption,
    Question,
    Tool,
    ToolAnswer,
)
from apps.user.factories import UserFactory


class CatalogFactory(DjangoModelFactory[Catalog]):
    class Meta:  # type: ignore[reportMissingTypeArgument]
        model = Catalog

    name = Sequence(lambda n: f"Catalog {n}")
    description = "Catalog description"
    show_in_help_me_choose = False

    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)


class QuestionFactory(DjangoModelFactory[Question]):
    class Meta:  # type: ignore[reportMissingTypeArgument]
        model = Question

    catalog = SubFactory(CatalogFactory)

    title = Sequence(lambda n: f"Question {n}")
    short_name = Sequence(lambda n: f"question_{n}")
    description = "Question description"
    order = Sequence(lambda n: n + 1)

    # Ordinal labels
    label_na = "N/A"
    label_1 = "1"
    label_2 = "2"
    label_3 = "3"
    label_4 = "4"

    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)


class CheckboxOptionFactory(DjangoModelFactory[CheckboxOption]):
    class Meta:  # type: ignore[reportMissingTypeArgument]
        model = CheckboxOption

    text = Sequence(lambda n: f"Option {n}")
    order = Sequence(lambda n: n + 1)

    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)


class ToolFactory(DjangoModelFactory[Tool]):
    class Meta:  # type: ignore[reportMissingTypeArgument]
        model = Tool

    name = Sequence(lambda n: f"Tool {n}")
    tagline = Sequence(lambda n: f"Tagline {n}")
    description = "Tool description"

    video_link = None
    tool_link = None
    logo = None

    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)

    @factory.post_generation  # type: ignore[reportMissingTypeArgument]
    def catalogs(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for catalog in extracted:
                self.catalogs.add(catalog)  # type: ignore[reportMissingTypeArgument]


class ToolAnswerFactory(DjangoModelFactory[ToolAnswer]):
    class Meta:  # type: ignore[reportMissingTypeArgument]
        model = ToolAnswer

    created_by = SubFactory(UserFactory)
    modified_by = SubFactory(UserFactory)
