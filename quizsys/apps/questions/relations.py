from rest_framework import serializers, exceptions

from quizsys.apps.questions.models import Tag


class TagRelatedField(serializers.RelatedField):
    def get_queryset(self):
        return Tag.objects.all()

    def to_internal_value(self, data):
        """
        Transform the *incoming* primitive data into a native value.
        """
        question, created = Tag.objects.get_or_create(content=data)

        return question

    def to_representation(self, value):
        """
        Transform the *outgoing* native value into primitive data.
        """
        return value.content