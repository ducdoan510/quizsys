from django.db.models import Q, Count
from rest_framework import generics, status, exceptions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from quizsys.apps.questions.models import Question, Choice, Answer, TestCase, Tag
from quizsys.apps.questions.renderers import QuestionJSONRenderer, ChoiceJSONRenderer, AnswerJSONRenderer, \
    TestCaseJSONRenderer, TagJSONRenderer
from quizsys.apps.questions.serializers import QuestionSerializer, ChoiceSerializer, AnswerSerializer, \
    TestCaseSerializer, TagSerializer


class QuestionListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser, )
    renderer_classes = (QuestionJSONRenderer, )
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def create(self, request, *args, **kwargs):
        serializer_data = request.data.get('question', {})
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class QuestionsListByTagsAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)
    renderer_classes = (QuestionJSONRenderer,)
    serializer_class = QuestionSerializer

    def post(self, request):
        tag_contents = request.data.get('tagFilters', [])
        tags = Tag.objects.filter(content__in=tag_contents)
        filtered_questions = Question.objects.exclude(~Q(tags__in=tags))\
            .annotate(tag_count=Count('tags')).filter(tag_count__gte=tags.count())
        paginator = LimitOffsetPagination()
        page = paginator.paginate_queryset(filtered_questions, request)
        serializer = self.serializer_class(page, many=True)
        return Response({
            'results': serializer.data,
            'count': filtered_questions.count()
        }, status=status.HTTP_200_OK)


class QuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser, )
    renderer_classes = (QuestionJSONRenderer, )
    serializer_class = QuestionSerializer
    lookup_url_kwarg = 'question_pk'

    def retrieve(self, request, question_pk=None):
        try:
            question = Question.objects.get(pk=question_pk)
        except Question.DoesNotExist:
            raise exceptions.NotFound("Question does not exist")
        serializer = self.serializer_class(question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, question_pk=None):
        try:
            question = Question.objects.get(pk=question_pk)
        except Question.DoesNotExist:
            raise exceptions.NotFound("Question does not exist")
        serializer_data = request.data.get('question', {})
        serializer = self.serializer_class(question, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, question_pk=None):
        try:
            question = Question.objects.get(pk=question_pk)
        except Question.DoesNotExist:
            raise exceptions.NotFound("Question does not exist")
        question.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class QuestionResponseListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'question__pk'
    lookup_field_kwarg = 'question_pk'
    permission_classes = (IsAuthenticated, IsAdminUser, )

    def filter_queryset(self, queryset):
        filters = {self.lookup_field: self.kwargs[self.lookup_field_kwarg]}
        return queryset.filter(**filters)

    def create(self, request, question_pk=None):
        try:
            question = Question.objects.get(pk=question_pk)
        except Question.DoesNotExist:
            raise exceptions.NotFound("Question does not exist")

        serializer_context = {'question': question}
        serializer_data = request.data.get(self.response_key, {})
        serializer = self.serializer_class(data=serializer_data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.filter_queryset(self.get_queryset()), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionResponseUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser, )

    def update(self, request, *args, **kwargs):
        response_pk = self.kwargs.get(self.response_pk_kwarg, None)
        try:
            response_obj = self.response_class.objects.get(pk=response_pk)
        except self.response_class.DoesNotExist:
            raise exceptions.NotFound("%s does not exist" % self.response_class.__name__)

        serializer_data = request.data.get(self.response_key, {})
        serializer = self.serializer_class(response_obj, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        response_pk = self.kwargs.get(self.response_pk_kwarg, None)
        try:
            response_obj = self.response_class.objects.get(pk=response_pk)
        except self.response_class.DoesNotExists:
            raise exceptions.NotFound("%s does not exist" % self.response_class.__class__.__name__)
        response_obj.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ChoiceListCreateAPIView(QuestionResponseListCreateAPIView):
    serializer_class = ChoiceSerializer
    renderer_classes = (ChoiceJSONRenderer, )
    response_key = 'choice'
    queryset = Choice.objects.select_related('question')


class ChoiceUpdateDestroyAPIView(QuestionResponseUpdateDestroyAPIView):
    serializer_class = ChoiceSerializer
    renderer_classes = (ChoiceJSONRenderer, )
    response_pk_kwarg = 'choice_pk'
    response_class = Choice
    response_key = 'choice'

class AnswerListCreateAPIView(QuestionResponseListCreateAPIView):
    serializer_class = AnswerSerializer
    renderer_classes = (AnswerJSONRenderer, )
    response_key = 'answer'
    queryset = Answer.objects.select_related('question')


class AnswerUpdateDestroyAPIView(QuestionResponseUpdateDestroyAPIView):
    serializer_class = AnswerSerializer
    renderer_classes = (AnswerJSONRenderer, )
    response_pk_kwarg = 'answer_pk'
    response_class = Answer
    response_key = 'answer'


class TestCaseListCreateAPIView(QuestionResponseListCreateAPIView):
    serializer_class = TestCaseSerializer
    renderer_classes = (TestCaseJSONRenderer, )
    response_key = 'testcase'
    queryset = TestCase.objects.select_related('question')


class TestCaseUpdateDestroyAPIView(QuestionResponseUpdateDestroyAPIView):
    serializer_class = TestCaseSerializer
    renderer_classes = (TestCaseJSONRenderer,)
    response_pk_kwarg = 'testcase_pk'
    response_class = TestCase
    response_key = 'testcase'


class TagListAPIView(generics.ListAPIView):
    serializer_class = TagSerializer
    renderer_classes = (TagJSONRenderer,)
    permission_classes = (IsAuthenticated, IsAdminUser,)
    queryset = Tag.objects.all()

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
