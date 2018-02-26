from django.db import models

from quizsys.apps.core.models import TimestampedModel


class Quiz(TimestampedModel):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True)
    title = models.CharField(max_length=20, unique=True)
    questions_per_page = models.PositiveIntegerField(default=1)
    labgroup = models.ForeignKey('users.Group', on_delete=models.SET_NULL, related_name='quizzes', null=True)
    pass_score = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = 'quizzes'
        ordering = ['-start_time']

    @property
    def number_of_questions(self):
        return self.score_distributions.count()

    @property
    def total_points(self):
        return self.score_distributions.aggregate(models.Sum('point'))['point__sum']

    @property
    def average_scores(self):
        quiz_submissions = self.quiz_submissions
        for quiz_submission in quiz_submissions.all():
            if not quiz_submission.is_graded:
                return "Grading in progress..."
        return str(quiz_submissions.aggregate(models.Avg('score'))['score__avg'])


class ScoreDistribution(TimestampedModel):
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE, related_name='score_distributions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='score_distributions')
    point = models.FloatField() # used for grading


class QuizSubmission(TimestampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_submissions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='quiz_submissions')
    score = models.FloatField(default=0)

    @property
    def is_graded(self):
        for question_submission in self.question_submissions.all():
            if not question_submission.is_graded:
                return False
        return True


class QuestionSubmission(TimestampedModel):
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE, related_name='question_submissions')
    quiz_submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='question_submissions')
    is_correct = models.BooleanField(default=False)
    is_graded = models.BooleanField(default=False)
    response = models.TextField(blank=True)

