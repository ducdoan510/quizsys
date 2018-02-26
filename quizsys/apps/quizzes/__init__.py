from django.apps import AppConfig


class QuizAppConfig(AppConfig):
    name = 'quizsys.apps.quizzes'
    label = 'quizzes'
    verbose_name = 'Quizzes'

    def ready(self):
        import quizsys.apps.quizzes.signals

default_app_config = 'quizsys.apps.quizzes.QuizAppConfig'
