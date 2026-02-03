import typing

from django.db import transaction
from django.utils.translation import gettext
from rest_framework import serializers

from apps.tool_picker.models import (
    CheckboxOption,
    QuestionTypeEnum,
    UserAnswer,
    UserSubmission,
)

from .utils import calculate_recommendations


class UserAnswerSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CheckboxOption.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = UserAnswer
        fields = (
            "question",
            "ordinal_value",
            "selected_options",
        )

    @typing.override
    def validate(self, attrs: dict[str, typing.Any]):
        question = attrs.get("question")
        ordinal_value = attrs.get("ordinal_value")
        selected_options = attrs.get("selected_options", [])

        if not question:
            raise serializers.ValidationError(
                gettext("Question is required."),
            )

        if question.question_type == QuestionTypeEnum.ORDINAL:
            if not ordinal_value:
                raise serializers.ValidationError(
                    {
                        "ordinal_value": gettext(
                            "Selected question is %s type question and requires an ordinal value.",
                        )
                        % question.get_question_type_display(),
                    },
                )

            if selected_options:
                raise serializers.ValidationError(
                    {
                        "selected_options": gettext(
                            "Selected question is %s type question and should not have selected options.",
                        )
                        % question.get_question_type_display(),
                    },
                )

        elif question.question_type == QuestionTypeEnum.CHECKBOX:
            if not selected_options:
                raise serializers.ValidationError(
                    {
                        "selected_options": gettext(
                            "Selected question is %s type question and requires selected options.",
                        )
                        % question.get_question_type_display(),
                    },
                )

            if ordinal_value:
                raise serializers.ValidationError(
                    {
                        "ordinal_value": gettext(
                            "Selected question is %s and should not have an ordinal value.",
                        )
                        % question.get_question_type_display(),
                    },
                )

            invalid_options = [opt for opt in selected_options if opt.question_id != question.id]
            if invalid_options:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": gettext(
                            "Some selected options do not belong to the %s question.",
                        )
                        % question.get_question_type_display(),
                    },
                )

        else:
            raise serializers.ValidationError(
                {
                    "non_field_errors": gettext(
                        "Unsupported question type",
                    ),
                },
            )

        return attrs


class UserSubmissionSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, write_only=True)

    class Meta:
        model = UserSubmission
        fields = (
            "id",
            "catalog",
            "answers",
        )

    @transaction.atomic
    @typing.override
    def create(self, validated_data: dict[str, typing.Any]):
        answers_data = validated_data.pop("answers")
        submission = super().create(validated_data)

        answers = [
            UserAnswer(
                submission=submission,
                question=answer["question"],
                ordinal_value=answer.get("ordinal_value")
                if answer["question"].question_type == QuestionTypeEnum.ORDINAL
                else None,
            )
            for answer in answers_data
        ]
        created_answers = UserAnswer.objects.bulk_create(answers)

        for user_answer, answer in zip(created_answers, answers_data, strict=True):
            if answer["question"].question_type == QuestionTypeEnum.CHECKBOX:
                selected_options = answer.get("selected_options", [])
                if selected_options:
                    user_answer.selected_options.add(*selected_options)
        calculate_recommendations(submission)
        return submission
