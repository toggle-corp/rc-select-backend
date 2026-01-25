from rest_framework import serializers

from .models import UserAnswer


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = (
            "catalog",
            "question",
            "ordinal_value",
        )
