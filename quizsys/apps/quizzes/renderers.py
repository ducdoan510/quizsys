from quizsys.apps.core.renderers import QuizsysJSONRenderer, QuizsysPaginationJSONRenderer


class QuizJSONRenderer(QuizsysPaginationJSONRenderer):
    object_label = 'quiz'
    object_label_plural = 'quizzes'
    count_label = 'quizzesCount'


class ScoreDistributionJSONRenderer(QuizsysJSONRenderer):
    object_label = 'score_distribution'
    object_label_plural = 'score_distributions'


class QuizSubmissionJSONRenderer(QuizsysPaginationJSONRenderer):
    object_label = 'quiz_submission'
    object_label_plural = 'quiz_submissions'
    count_label = 'quizSubmissionsCount'


class QuestionSubmissionJSONRenderer(QuizsysJSONRenderer):
    object_label = 'question_submission'
    object_label_plural = 'question_submissions'

