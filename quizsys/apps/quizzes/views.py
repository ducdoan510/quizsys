import re
from datetime import timedelta

from django.core.mail import send_mail, send_mass_mail
from django.db.models import F
from django.utils import timezone

from rest_framework import generics, status, exceptions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from quizsys.apps.questions.models import Question
from quizsys.apps.questions.renderers import QuestionJSONRenderer, QuestionAllJSONRenderer
from quizsys.apps.questions.serializers import QuestionSerializer
from quizsys.apps.quizzes.models import Quiz, QuizSubmission, ScoreDistribution, Announcement
from quizsys.apps.quizzes.renderers import QuizJSONRenderer, QuizSubmissionJSONRenderer, ScoreDistributionJSONRenderer, \
    AnnouncementJSONRenderer
from quizsys.apps.quizzes.serializers import QuizSerializer, QuizSubmissionSerializer, ScoreDistributionSerializer, \
    AnnouncementSerializer
from quizsys.apps.users.models import User
from quizsys.apps.users.renderers import UserJSONRenderer, UserAllJSONRenderer
from quizsys.apps.users.serializers import UserSerializer


class QuizListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (QuizJSONRenderer,)
    serializer_class = QuizSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Quiz.objects.all()
        return self.request.user.group.quizzes.all()

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({
                "errors": {
                    "detail": "You are not allowed to perform this action"
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer_data = request.data.get('quiz', {})
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class QuizFilteredListAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)
    renderer_classes = (QuizSubmissionJSONRenderer,)
    serializer_class = QuizSubmissionSerializer

    def post(self, request):
        filters = request.data.get('filters', None)
        filtered_quizzes = QuizSubmission.objects.all()
        if filters:
            quiz_title = filters.get('quizTitle', None)
            username = filters.get('username', None)
            passFail = filters.get('passFail', None)

            if quiz_title:
                filtered_quizzes = filtered_quizzes.filter(quiz__title=quiz_title)
            if username:
                filtered_quizzes = filtered_quizzes.filter(user__username=username)
            if passFail == "Pass":
                filtered_quizzes = filtered_quizzes.filter(score__gte=F('quiz__pass_score'))
            if passFail == "Fail":
                filtered_quizzes = filtered_quizzes.filter(score__lt=F('quiz__pass_score'))

        paginator = LimitOffsetPagination()
        page = paginator.paginate_queryset(filtered_quizzes, request)
        serializer = self.serializer_class(page, many=True)
        return Response({
            'results': serializer.data,
            'count': filtered_quizzes.count()
        }, status=status.HTTP_200_OK)


class QuizRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (QuizJSONRenderer, )
    serializer_class = QuizSerializer
    lookup_url_kwarg = 'quiz_pk'

    def retrieve(self, request, quiz_pk=None):
        try:
            if request.user.is_staff:
                quiz = Quiz.objects.get(pk=quiz_pk)
            else:
                quiz = request.user.group.quizzes.get(pk=quiz_pk)
        except Quiz.DoesNotExist:
            raise exceptions.NotFound("Quiz does not exist")

        # quiz_submission = None
        # try:
        #     if not request.user.is_staff:
        #         quiz_submission = quiz.quiz_submissions.get(user=request.user)
        # except QuizSubmission.DoesNotExist:
        #     quiz_submission = None
        #
        # if quiz_submission is not None:
        #     serializer = QuizSubmissionSerializer(quiz_submission)
        #     return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.serializer_class(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, quiz_pk=None):
        if request.user.is_staff:
            try:
                quiz = Quiz.objects.get(pk=quiz_pk)
            except Quiz.DoesNotExist:
                raise exceptions.NotFound("Quiz does not exist")

            serializer_data = request.data.get('quiz', {})
            serializer = self.serializer_class(quiz, data=serializer_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, quiz_pk=None):
        if request.user.is_staff:
            try:
                quiz = Quiz.objects.get(pk=quiz_pk)
            except Quiz.DoesNotExist:
                raise exceptions.NotFound("Quiz does not exist")
            quiz.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class QuizQuestionsListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (QuestionAllJSONRenderer,)
    serializer_class = QuestionSerializer

    def get_queryset(self):
        try:
            quiz = Quiz.objects.get(pk=self.kwargs['quiz_pk'])
        except Quiz.DoesNotExist:
            raise exceptions.NotFound("Quiz does not exist")

        question_pks = quiz.score_distributions.select_related('question').values('question')
        return Question.objects.filter(pk__in=question_pks)

    def list(self, request, *args, **kwargs):
        try:
            quiz = Quiz.objects.get(pk=self.kwargs['quiz_pk'])
        except Quiz.DoesNotExist:
            raise exceptions.NotFound("Quiz does not exist")

        print(timezone.now())
        print(quiz.start_time)
        if (not self.request.user.is_staff) and (timezone.now() < quiz.start_time):
            # quiz.start_time.astimezone(local_tz).strftime("%Y-%m-%d %H:%M:%S%Z")
            return Response({
                "errors": {
                    "detail": "This quiz has not started"
                }
            }, status=status.HTTP_202_ACCEPTED)

        # if (not self.request.user.is_staff) and (timezone.now() > quiz.end_time):
        #     # quiz.start_time.astimezone(local_tz).strftime("%Y-%m-%d %H:%M:%S%Z")
        #     return Response({
        #         "errors": {
        #             "detail": "This quiz has finished"
        #         }
        #     }, status=status.HTTP_202_ACCEPTED)

        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # page = self.paginate_queryset(queryset)
        # serializer = self.serializer_class(page, many=True)
        # return self.get_paginated_response(serializer.data)


class ScoreDistributionListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ScoreDistributionSerializer
    renderer_classes = (ScoreDistributionJSONRenderer,)

    def get_queryset(self):
        try:
            quiz = Quiz.objects.get(pk=self.kwargs['quiz_pk'])
        except Quiz.DoesNotExist:
            raise exceptions.NotFound('Quiz does not exist')
        return quiz.score_distributions

    def create(self, request, quiz_pk=None):
        try:
            quiz = Quiz.objects.get(pk=quiz_pk)
        except Quiz.DoesNotExist:
            raise exceptions.NotFound("Quiz does not exist")

        serializer_context = {'quiz': quiz}
        serializer_data = request.data.get('score_distribution', {})
        serializer = self.serializer_class(data=serializer_data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScoreDistributionDestroyAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)
    serializer_class = ScoreDistributionSerializer
    renderer_classes = (ScoreDistributionJSONRenderer,)

    def destroy(self, request, *args, **kwargs):
        score_pk = self.kwargs.get('score_pk', None)
        try:
            score_obj = ScoreDistribution.objects.get(pk=score_pk)
        except ScoreDistribution.DoesNotExist:
            raise exceptions.NotFound('ScoreDistribution does not exist')
        score_obj.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class QuizSubmissionListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (QuizSubmissionJSONRenderer,)
    serializer_class = QuizSubmissionSerializer

    def get_queryset(self):
        try:
            quiz = Quiz.objects.get(pk=self.kwargs['quiz_pk'])
        except Quiz.DoesNotExist:
            raise exceptions.NotFound("Quiz does not exist")

        if self.request.user.is_staff:
            return QuizSubmission.objects.filter(quiz=quiz)
        return QuizSubmission.objects.filter(quiz=quiz, user=self.request.user)

    def create(self, request, quiz_pk=None):
        try:
            quiz = Quiz.objects.get(pk=quiz_pk)
        except Quiz.DoesNotExist:
            raise exceptions.NotFound("Quiz does not exist")

        serializer_context = {
            'quiz': quiz,
            'user': request.user
        }

        # if timezone.now() > quiz.end_time:
        #     return Response({
        #         'errors': {
        #             'detail': 'Deadline for this quiz has passed'
        #         }
        #     }, status=status.HTTP_400_BAD_REQUEST)

        if QuizSubmission.objects.filter(quiz=quiz, user=request.user).count() > 0:
            return Response({
                'errors': {
                    'detail': 'User already submitted for this quiz'
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer_data = request.data.get('quiz_submission', {})
        serializer = self.serializer_class(data=serializer_data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class QuizSubmissionRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (QuizSubmissionJSONRenderer,)
    serializer_class = QuizSubmissionSerializer

    def retrieve(self, request, quiz_submission_pk=None, quiz_pk=None, username=None):
        if quiz_submission_pk:
            try:
                quiz_submission = QuizSubmission.objects.get(pk=quiz_submission_pk)
            except QuizSubmission.DoesNotExist:
                raise exceptions.NotFound("Quiz submission doest not exist")
        else:
            try:
                user = User.objects.get(username=username)
                quiz_submission = QuizSubmission.objects.get(quiz=quiz_pk, user=user)
            except User.DoesNotExist:
                raise exceptions.NotFound("User does not exist")
            except QuizSubmission.DoesNotExist:
                return Response({
                        'quiz_submission': {
                            'question_submissions': []
                        }
                    }
                )

        serializer = self.serializer_class(quiz_submission)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizSubmissionAllListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (QuizSubmissionJSONRenderer,)
    serializer_class = QuizSubmissionSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return QuizSubmission.objects.all()
        return self.request.user.quiz_submissions.all()

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class QuizFailedUsersAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)
    renderer_classes = (UserAllJSONRenderer,)
    serializer_class = UserSerializer

    def post(self, request):
        try:
            quiz = Quiz.objects.get(title=request.data.get('quizTitle', '').strip())
        except Quiz.DoesNotExist:
            raise exceptions.NotFound("Quiz does not exist")

        print(quiz)
        pass_score = quiz.pass_score
        failed_quiz_user_ids = [item['user'] for item in QuizSubmission.objects.filter(quiz=quiz, score__lt=pass_score).values('user')]
        failed_quiz_users = User.objects.filter(pk__in=failed_quiz_user_ids)
        serializer = self.serializer_class(failed_quiz_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendEmailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def post(self, request):
        from_email = request.data.get('from_email', '')
        to_emails = request.data.get('to_emails', '').split(";")
        to_emails = [email.strip() for email in to_emails if email != '']
        for email in to_emails:
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                return Response({
                    'errors': {
                        'detail': 'Invalid email(s) detected'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        title = request.data.get('title', '')
        content = request.data.get('content', '')

        try:
            send_mail(title, content, from_email, to_emails, fail_silently=False)
        except:
            return Response({
                'errors': {
                    'detail': 'Email not delivered'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnnouncementListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AnnouncementSerializer
    renderer_classes = (AnnouncementJSONRenderer,)

    def get_queryset(self):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise exceptions.NotFound('User does not exist')
        return Announcement.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

