import typing

from captcha.serializers import CaptchaModelSerializer
from django.db import transaction
from rest_framework import serializers

from apps.resources.models import ContactRequest, RequestDemo
from apps.tool_picker.models import Tool

from .tasks import send_contact_request_email, send_demo_request_email


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
        instance = super().create(validated_data)
        transaction.on_commit(
            lambda: send_contact_request_email.delay(instance.id),  # type: ignore[reportIncompatibleVariableOverride]
        )
        return instance


class RequestDemoSerializer(CaptchaModelSerializer):
    captcha_code = serializers.CharField(write_only=True)
    captcha_hashkey = serializers.CharField(write_only=True)

    tool = serializers.PrimaryKeyRelatedField(
        queryset=Tool.objects.all(),
    )

    class Meta:
        model = RequestDemo
        fields = (
            "name",
            "email",
            "national_society",
            "content",
            "tool",
            "captcha_code",
            "captcha_hashkey",
        )

    @typing.override
    def create(self, validated_data: dict[str, typing.Any]):
        validated_data.pop("captcha_code", None)
        validated_data.pop("captcha_hashkey", None)
        instance = super().create(validated_data)
        transaction.on_commit(
            lambda: send_demo_request_email.delay(instance.id),  # type: ignore[reportIncompatibleVariableOverride]
        )
        return instance
