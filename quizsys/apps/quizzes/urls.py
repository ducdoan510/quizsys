from django.conf.urls import url

from quizsys.apps.quizzes.views import QuizListCreateAPIView, QuizRetrieveUpdateDestroyAPIView, \
    QuizSubmissionListCreateAPIView, QuizSubmissionRetrieveAPIView, ScoreDistributionListCreateAPIView, \
    ScoreDistributionDestroyAPIView, QuizQuestionsListAPIView, QuizSubmissionAllListAPIView, QuizFilteredListAPIView, \
    SendEmailAPIView, QuizFailedUsersAPIView, AnnouncementListAPIView

app_name = 'quizzes'

urlpatterns = {
    url(r'^quizzes/?$', QuizListCreateAPIView.as_view()),
    url(r'^quiz/(?P<quiz_pk>\d+)/?$', QuizRetrieveUpdateDestroyAPIView.as_view()),
    url(r'^quiz/(?P<quiz_pk>\d+)/score-distributions/?$', ScoreDistributionListCreateAPIView.as_view()),
    url(r'^quiz/(?P<quiz_pk>\d+)/score-distributions/(?P<score_pk>\d+)/?$', ScoreDistributionDestroyAPIView.as_view()),
    url(r'^quiz/(?P<quiz_pk>\d+)/questions/?$', QuizQuestionsListAPIView.as_view()),

    url(r'^quiz/(?P<quiz_pk>\d+)/quiz-submissions/?$', QuizSubmissionListCreateAPIView.as_view()),
    url(r'^quiz-submissions/(?P<quiz_submission_pk>\d+)/?$', QuizSubmissionRetrieveAPIView.as_view()),
    url(r'^quiz-submissions/quiz/(?P<quiz_pk>\d+)/user/(?P<username>[\w]+)/?$', QuizSubmissionRetrieveAPIView.as_view()),
    url(r'^quiz-submissions/?$', QuizSubmissionAllListAPIView.as_view()),
    url(r'^quiz-submissions-filtered/?$', QuizFilteredListAPIView.as_view()),

    url(r'^send-email/?', SendEmailAPIView.as_view()),
    url(r'^quiz-failed-users/?', QuizFailedUsersAPIView.as_view()),

    url(r'^announcements/(?P<username>[\w]+)/?$', AnnouncementListAPIView.as_view()),
}