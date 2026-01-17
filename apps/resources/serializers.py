from rest_framework import serializers
from apps.resources.models import ContactRequest

class ContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = (
            "name",
            "email",
            "national_society",
            "content",
        )
