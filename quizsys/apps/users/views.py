import time

import pandas
from django.core.files.base import ContentFile
from rest_framework import status, generics, exceptions
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from quizsys.apps.core.permissions import IsStaffOrSelf
from quizsys.apps.users.models import User, Group
from quizsys.apps.users.renderers import UserJSONRenderer, GroupJSONRenderer
from quizsys.apps.users.serializers import UserSerializer, RegistrationSerializer, LoginSerializer, GroupSerializer

from django.core.files.storage import default_storage


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny, )
    renderer_classes = (UserJSONRenderer, )
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer_data = request.data.get('user', {})
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny, )
    renderer_classes = (UserJSONRenderer, )
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsStaffOrSelf, )
    renderer_classes = (UserJSONRenderer, )
    serializer_class = UserSerializer
    lookup_url_kwarg = 'username'
    lookup_field = 'username'

    def retrieve(self, request, *args, **kwargs):
        lookup_condition = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        try:
            user = User.objects.get(**lookup_condition)
        except User.DoesNotExist:
            raise exceptions.NotFound("User does not exist")
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        lookup_condition = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        try:
            user = User.objects.get(**lookup_condition)
        except User.DoesNotExist:
            raise exceptions.NotFound("User does not exist")
        serializer_data = request.data.get('user', {})
        serializer = self.serializer_class(user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, username=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.NotFound("User does not exist")
        user.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class CurrentUserRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (UserJSONRenderer, )
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class UserUploadAPIView(APIView):
    # parser_classes = (FileUploadParser,)
    permission_classes = (AllowAny,)

    def put(self, request, filename, format=None):
        # file_obj = request.data['file']
        # path = default_storage.save('demo.csv', ContentFile(file_obj.read()))
        # print(path)

        try:
            for file in request.FILES.values():
                book = pandas.ExcelFile(file)
            for sheet_name in book.sheet_names:
                # print(sheet_name)
                # print(book.parse(sheet_name))
                group, created = Group.objects.get_or_create(name=sheet_name)
                user_list = book.parse(sheet_name)
                print(user_list.columns)
                for index, column in user_list.iterrows():
                    student_name = user_list.iloc[index]['Name']
                    if len(student_name) == 0:
                        continue
                    username = (sheet_name + "_" + "_".join(student_name.strip().split())).upper()
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        user = User.objects.create_user(username=username, password=username)
                        user.group = group
                        user.save()
        except Exception as exc:
            print(exc)
            return Response({
                'errors': {
                    'detail': 'Some error occurred. Please check the file or read the instruction again.'
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)
    renderer_classes = (GroupJSONRenderer, )
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def create(self, request, *args, **kwargs):
        serializer_data = request.data.get('group', {})
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class GroupRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)
    renderer_classes = (GroupJSONRenderer,)
    serializer_class = GroupSerializer

    def retrieve(self, request, group_name=None):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise exceptions.NotFound("Group does not exist")
        serializer = self.serializer_class(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, group_name=None):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise exceptions.NotFound("Group does not exist")
        serializer_data = request.data.get('group', {})
        serializer = self.serializer_class(group, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, group_name=None):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise exceptions.NotFound("Group does not exist")
        group.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)




