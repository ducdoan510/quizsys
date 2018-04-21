from dateutil import tz
from rest_framework import serializers

from quizsys.apps.core.relations import CustomizedDateTimeField
from quizsys.apps.questions.models import Question
from quizsys.apps.quizzes.models import Quiz, ScoreDistribution, QuestionSubmission, QuizSubmission, Announcement
from quizsys.apps.quizzes.relations import QuestionRelatedField, QuizRelatedField
from quizsys.apps.users.relations import UserRelatedField, GroupRelatedField


class ScoreDistributionSerializer(serializers.ModelSerializer):
    question = QuestionRelatedField()
    pk = serializers.IntegerField(read_only=True)

    class Meta:
        model = ScoreDistribution
        fields = ('pk', 'question', 'point',)

    def create(self, validated_data):
        quiz = self.context['quiz']
        print(validated_data)
        question = validated_data['question']
        try:
            existing_score_distribution = ScoreDistribution.objects.get(question=question, quiz=quiz)
            existing_score_distribution.point = validated_data['point']
            existing_score_distribution.save()
            return existing_score_distribution
        except ScoreDistribution.DoesNotExist:
            return ScoreDistribution.objects.create(quiz=quiz, **validated_data)


class QuizSerializer(serializers.ModelSerializer):
    labgroup = GroupRelatedField()
    # score_distributions = ScoreDistributionSerializer(many=True, required=False)
    pk = serializers.IntegerField(read_only=True)
    number_of_questions = serializers.IntegerField(read_only=True)
    total_points = serializers.FloatField(read_only=True)
    start_time = CustomizedDateTimeField()
    end_time = CustomizedDateTimeField()
    answer_release_time = CustomizedDateTimeField()
    quiz_status = serializers.CharField(max_length=20, read_only=True)

    class Meta:
        model = Quiz
        fields = ('pk', 'start_time', 'end_time', 'answer_release_time', 'description', 'title', 'quiz_status',
                  'labgroup', 'questions_per_page', 'number_of_questions', 'total_points', 'pass_score', 'push_notification')

    def create(self, validated_data):
        score_distributions = validated_data.pop('score_distributions', [])
        quiz = Quiz.objects.create(**validated_data)

        for score_distribution in score_distributions:
            ScoreDistribution.objects.create(quiz=quiz, **score_distribution)

        return quiz

    def update(self, instance, validated_data):
        score_distributions = validated_data.pop('score_distributions', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        score_distributions_queryset = instance.score_distributions
        for score_distribution in score_distributions:
            question = score_distribution['question']
            try:
                score_distribution_obj = score_distributions_queryset.get(question=question)
                setattr(score_distribution_obj, 'point', score_distribution['point'])
                score_distribution_obj.save()
            except ScoreDistribution.DoesNotExist:
                ScoreDistribution.objects.create(quiz=instance, **score_distribution)

        instance.save()
        return instance


class QuestionSubmissionSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    pk = serializers.IntegerField(read_only=True)
    is_correct = serializers.BooleanField(read_only=True)
    extra_info = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = QuestionSubmission
        fields = ('pk', 'question', 'is_correct', 'response', 'extra_info')


class QuizSubmissionSerializer(serializers.ModelSerializer):
    quiz = QuizRelatedField(read_only=True)
    user = UserRelatedField(read_only=True)
    score = serializers.FloatField(read_only=True)
    pk = serializers.IntegerField(read_only=True)
    question_submissions = QuestionSubmissionSerializer(many=True)
    is_graded = serializers.BooleanField(read_only=True)
    average_scores = serializers.CharField(max_length=63, read_only=True, source='quiz.average_scores')
    pass_score = serializers.FloatField(source='quiz.pass_score', read_only=True)

    class Meta:
        model = QuizSubmission
        fields = ('pk', 'quiz', 'user', 'score', 'question_submissions', 'is_graded', 'average_scores',
                  'pass_score')

    def create(self, validated_data):
        user = self.context['user']
        quiz = self.context['quiz']
        question_submissions = validated_data.pop('question_submissions', [])
        quiz_submission = QuizSubmission.objects.create(user=user, quiz=quiz, **validated_data)

        for question_submission in question_submissions:
            QuestionSubmission.objects.create(quiz_submission=quiz_submission, **question_submission)

        if quiz_submission.is_graded and quiz_submission.quiz.push_notification and quiz_submission.score < quiz_submission.quiz.pass_score:
            content = "You did not score enough to pass the quiz '%s'. All the best for the next quiz."
            Announcement.objects.create(user=quiz_submission.user, content=content % quiz_submission.quiz.title)

        return quiz_submission


class AnnouncementSerializer(serializers.ModelSerializer):
    user = UserRelatedField()
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Announcement
        fields = ('user', 'content', 'is_read', 'id')