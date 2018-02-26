from rest_framework import serializers, exceptions

from .models import User, Group


class UserRelatedField(serializers.RelatedField):
    def get_queryset(self):
        return User.objects.all()

    def to_internal_value(self, data):
        """
        Transform the *incoming* primitive data into a native value.
        """
        try:
            user = User.objects.get(username=data)
        except User.DoesNotExist:
            raise exceptions.NotFound("User does not exist")
        return user

    def to_representation(self, value):
        """
        Transform the *outgoing* native value into primitive data.
        """
        return value.username


class GroupRelatedField(serializers.RelatedField):
    def get_queryset(self):
        return Group.objects.all()

    def to_internal_value(self, data):
        try:
            group = Group.objects.get(name=data)
        except Group.DoesNotExist:
            raise exceptions.NotFound("Group does not exist")
        return group

    def to_representation(self, value):
        return value.name