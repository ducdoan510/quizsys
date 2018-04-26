from django.db.models.signals import post_save
from django.dispatch import receiver

from quizsys.apps.quizzes.models import QuestionSubmission
from quizsys.task_queue.new_task import grade_quiz_submission_task


@receiver(post_save, sender=QuestionSubmission)
def grade_and_update_quiz_score(sender, instance, created, *args, **kwargs):
    if instance.is_graded:
        return

    grade_quiz_submission_task(str(instance.pk))
