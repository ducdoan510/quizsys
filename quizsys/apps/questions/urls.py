from django.conf.urls import url

from quizsys.apps.questions.views import (
    QuestionListCreateAPIView, QuestionRetrieveUpdateDestroyAPIView,
    ChoiceListCreateAPIView, ChoiceUpdateDestroyAPIView,
    AnswerListCreateAPIView, AnswerUpdateDestroyAPIView, TestCaseListCreateAPIView, TestCaseUpdateDestroyAPIView,
    TagListAPIView, QuestionsListByTagsAPIView)

app_name = 'questions'

urlpatterns = [
    # question views
    url(r'^questions/?$', QuestionListCreateAPIView.as_view()),
    url(r'^question/(?P<question_pk>\d+)/?$', QuestionRetrieveUpdateDestroyAPIView.as_view()),
    url(r'^questions/by-tags/?$', QuestionsListByTagsAPIView.as_view()),
    # choice views
    url(r'^question/(?P<question_pk>\d+)/choices/?$', ChoiceListCreateAPIView.as_view()),
    url(r'^question/(?P<question_pk>\d+)/choices/(?P<choice_pk>\d+)/?$', ChoiceUpdateDestroyAPIView.as_view()),
    # answer views
    url(r'^question/(?P<question_pk>\d+)/answers/?$', AnswerListCreateAPIView.as_view()),
    url(r'^question/(?P<question_pk>\d+)/answers/(?P<answer_pk>\d+)/?$', AnswerUpdateDestroyAPIView.as_view()),
    # testcase views
    url(r'^question/(?P<question_pk>\d+)/testcases/?$', TestCaseListCreateAPIView.as_view()),
    url(r'^question/(?P<question_pk>\d+)/testcases/(?P<testcase_pk>\d+)/?$', TestCaseUpdateDestroyAPIView.as_view()),
    # tag views
    url(r'^tags/?$', TagListAPIView.as_view())
]