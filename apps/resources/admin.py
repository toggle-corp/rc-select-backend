# Register your models here.
from django.contrib import admin

from apps.resources.models import CaseStudy, ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin[ContactRequest]):
    list_display = ("name", "email", "national_society", "created_at")
    search_fields = ("name", "email")


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin[CaseStudy]):
    list_display = ("title",)
    search_fields = ("title",)
    list_select_related = ("tool",)
    autocomplete_fields = ("tool",)
