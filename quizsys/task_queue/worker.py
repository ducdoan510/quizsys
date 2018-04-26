import pika
import time

import os
from django.conf import settings
from django.apps import apps
from decouple import config

from quizsys.apps.questions.graders import grade_question

conf = {
    'INSTALLED_APPS' : [
         'rest_framework',
         'corsheaders',
         'django.contrib.admin',
         'django.contrib.auth',
         'django.contrib.contenttypes',
         'django.contrib.sessions',
         'django.contrib.messages',
         'django.contrib.staticfiles',

         'quizsys.apps.users',
         'quizsys.apps.questions',
         'quizsys.apps.quizzes',
     ],
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }
}
settings.configure(**conf)
apps.populate(settings.INSTALLED_APPS)


from quizsys.apps.quizzes.models import QuestionSubmission, ScoreDistribution

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)


def callback(ch, method, properties, body):
    print("[x] Received question submission pk: %r" % body)

    instance = QuestionSubmission.objects.get(pk=body.decode())

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
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='task_queue')

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
