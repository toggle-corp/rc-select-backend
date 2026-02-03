import typing

from captcha.serializers import CaptchaModelSerializer
from rest_framework import serializers

from apps.resources.models import ContactRequest


class ContactRequestSerializer(CaptchaModelSerializer):
    captcha_code = serializers.CharField(write_only=True)
    captcha_hashkey = serializers.CharField(write_only=True)

    class Meta:
        model = ContactRequest
        fields = (
            "name",
            "email",
            "national_society",
            "content",
            "captcha_code",
            "captcha_hashkey",
        )

    @typing.override
    def create(self, validated_data: dict[str, typing.Any]):
        validated_data.pop("captcha_code", None)
        validated_data.pop("captcha_hashkey", None)
        return super().create(validated_data)
