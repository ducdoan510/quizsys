from rest_framework import serializers, exceptions

from quizsys.apps.questions.models import Question
from quizsys.apps.quizzes.models import Quiz


class QuestionRelatedField(serializers.RelatedField):
    def get_queryset(self):
        return Question.objects.all()

    def to_internal_value(self, data):
        """
        Transform the *incoming* primitive data into a native value.
        """
        try:
            question = Question.objects.get(title=data)
        except:
            raise exceptions.NotFound("Question does not exist")
        return question

    def to_representation(self, value):
        """
        Transform the *outgoing* native value into primitive data.
        """
        return {
            "pk": value.pk,
            "title": value.title
        }


class QuizRelatedField(serializers.RelatedField):
    def get_queryset(self):
        return Quiz.objects.all()

    def to_internal_value(self, data):
        try:
            quiz = Quiz.objects.get(pk=data)
        except Quiz.DoesNotExist:
            raise exceptions.NotFound("Quiz does not exist")
        return quiz

    def to_representation(self, value):
        return value.title