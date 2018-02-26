from django.db.models.signals import post_save
from django.dispatch import receiver

from quizsys.apps.questions.graders import grade_question
from quizsys.apps.quizzes.models import QuestionSubmission, ScoreDistribution


@receiver(post_save, sender=QuestionSubmission)
def grade_and_update_quiz_score(sender, instance, created, *args, **kwargs):
    if instance.is_graded:
        return

    quiz_submission = instance.quiz_submission
    quiz = quiz_submission.quiz
    question = instance.question
    response = instance.response

    question_point = ScoreDistribution.objects.get(question=question, quiz=quiz).point
    response_correct = grade_question(question, response, file_suffix=instance.pk)["status"]

    quiz_submission.score += question_point * response_correct
    quiz_submission.save()

    instance.is_correct = response_correct
    instance.is_graded = True
    instance.save()
