import typing

from django.db import transaction
from django.utils.translation import gettext
from rest_framework import serializers

from apps.tool_picker.models import (
    CheckboxOption,
    OrdinalTypeEnum,
    Question,
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
            if ordinal_value:
                raise serializers.ValidationError(
                    {
                        "ordinal_value": gettext(
                            "Selected question is %s and should not have an ordinal value.",
                        )
                        % question.get_question_type_display(),
                    },
                )
        return attrs


class UserSubmissionSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, write_only=True, required=True)

    class Meta:
        model = UserSubmission
        fields = (
            "id",
            "catalog",
            "answers",
        )

    @typing.override
    def validate(self, attrs: dict[str, typing.Any]):
        catalog = attrs["catalog"]
        answers = attrs.get("answers", [])

        # All the question related to the selected catalog catalog.
        catalog_questions = set(
            catalog.questions.values_list("id", flat=True),
        )

        ordinal_answers = [ans for ans in answers if ans["question"].question_type == QuestionTypeEnum.ORDINAL]
        if ordinal_answers and all(ans["ordinal_value"] == OrdinalTypeEnum.NOT_AVAILABLE for ans in ordinal_answers):
            raise serializers.ValidationError(
                gettext("All ordinal answers should not be N/A. please choose one must be a different value."),
            )

        # All the question answered by user.
        answered_questions = {ans["question"].id for ans in answers}

        # Diff of related catalog question and user answered questions.
        missing_question = catalog_questions - answered_questions
        if missing_question:
            missing_question_titles = list(Question.objects.filter(id__in=missing_question).values_list("title", flat=True))
            raise serializers.ValidationError(
                {
                    "question": gettext(
                        "You must answer all questions related to the selected catalog. Missing questions are: %(missing)s",
                    )
                    % {"missing": (missing_question_titles)},
                },
            )

        return attrs

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
