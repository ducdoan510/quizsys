from django.db.models.signals import post_save
from django.dispatch import receiver

from quizsys.apps.questions.graders import grade_question
from quizsys.apps.quizzes.models import QuestionSubmission, ScoreDistribution, QuizSubmission, Announcement, Quiz
from quizsys.apps.users.models import User


@receiver(post_save, sender=QuestionSubmission)
def grade_and_update_quiz_score(sender, instance, created, *args, **kwargs):
    if instance.is_graded:
        return

    quiz_submission = instance.quiz_submission
    quiz = quiz_submission.quiz
    question = instance.question
    response = instance.response

    question_point = ScoreDistribution.objects.get(question=question, quiz=quiz).point
    grading_result = grade_question(question, response, file_suffix=instance.pk)
    response_correct = grading_result["status"]

    question_score = grading_result.pop('score', response_correct)
    quiz_submission.score += question_point * question_score
    quiz_submission.save()

    instance.is_correct = response_correct
    instance.is_graded = True
    instance.extra_info = grading_result.pop('extra_info', "")
    instance.save()


# @receiver(post_save, sender=Quiz)
# def push_reminder_notification(sender, instance, created, *args, **kwargs):
#     if created:
#         users = User.objects.filter(group=instance.labgroup)
#         # if created:
#         content = "You have a new quiz titled '%s' from %s to %s"
#         # else:
#         #     content = "Your quiz titled '%s' time is updated. New time is from %s to %s"
#         for user in users:
#             Announcement.objects.create(
#                 user=user,
#                 content=content % (instance.title, str(instance.start_time), str(instance.end_time))
#             )
