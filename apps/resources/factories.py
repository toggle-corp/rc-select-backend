from factory.django import DjangoModelFactory

from apps.resources.models import CaseStudy, ContactRequest


class ContactRequestFactory(DjangoModelFactory[ContactRequest]):
    class Meta:  # type: ignore[misc]
        model = ContactRequest


class CaseStudyFactory(DjangoModelFactory[CaseStudy]):
    class Meta:  # type: ignore[misc]
        model = CaseStudy
