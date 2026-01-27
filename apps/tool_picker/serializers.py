from rest_framework import serializers

from .models import CheckboxOption, UserAnswer


class UserAnswerSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CheckboxOption.objects.all(),
        required=False,
        allow_null=True,
    )
    ordinal_value = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = UserAnswer
        fields = (
            "catalog",
            "question",
            "ordinal_value",
            "selected_options",
        )
