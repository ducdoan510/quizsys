from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate

from quizsys.apps.users.models import User, Group
from quizsys.apps.users.relations import UserRelatedField


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=255,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    group = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'token', 'is_staff', 'group']

    def create(self, validated_data):
        group_name = validated_data.pop('group', None)
        print(group_name)
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                raise exceptions.NotFound('Group does not exists')
            user = User.objects.create_user(**validated_data)
            user.group = group
            user.save()
            return user
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    is_staff = serializers.BooleanField(read_only=True)

    def validate(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get('password', None)

        if username is None:
            raise serializers.ValidationError('Username is required to log in')
        if password is None:
            raise serializers.ValidationError('Password is required to log in')

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError('Username or password is incorrect')

        return {
            'username': user.username,
            'token': user.token,
            'is_staff': user.is_staff
        }


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=255,
        min_length=8,
        write_only=True,
        allow_blank=True
    )
    group = serializers.CharField(source='group.name')
    username = serializers.CharField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'token', 'group', 'is_staff', 'email')

    def update(self, instance, validated_data):
        print(validated_data)
        password = validated_data.pop('password', None)
        group = validated_data.pop('group', None)

        try:
            group_obj = Group.objects.get(name=group['name'])
        except Group.DoesNotExist:
            raise exceptions.NotFound("Group does not exist")

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.group = group_obj

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class GroupSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(read_only=True)
    users = UserRelatedField(many=True, required=False)

    class Meta:
        model = Group
        fields = ('pk', 'name', 'description', 'users',)

    def create(self, validated_data):
        usernames = validated_data.pop('users', None)

        group = Group.objects.create(**validated_data)
        if usernames is not None:
            for username in usernames:
                user = User.objects.get(username=username)
                if user:
                    user.group = group
                    user.save()
        return group

    def update(self, instance, validated_data):
        usernames = validated_data.pop('users')

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        for username in usernames:
            user = User.objects.get(username=username)
            if user:
                user.group = instance
                user.save()

        return instance