from rest_framework import serializers

from quizsys.apps.questions.exceptions import QuestionTypeMismatch
from quizsys.apps.questions.models import Choice, Answer, TestCase, Question, Tag
from quizsys.apps.questions.relations import TagRelatedField


class ChoiceSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    pk = serializers.IntegerField(read_only=True)

    class Meta:
        model = Choice
        fields = ('pk', 'question','content', 'is_correct_answer')

    def create(self, validated_data):
        question = self.context['question']
        if question.type != 'MCQ':
            raise QuestionTypeMismatch()
        return Choice.objects.create(question=question, **validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    pk = serializers.IntegerField(read_only=True)

    class Meta:
        model = Answer
        fields = ('pk', 'question', 'content')

    def create(self, validated_data):
        question = self.context['question']
        if question.type != 'FIB':
            raise QuestionTypeMismatch()
        return Answer.objects.create(question=question, **validated_data)


class TestCaseSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    pk = serializers.IntegerField(read_only=True)

    class Meta:
        model = TestCase
        fields = ('pk', 'question', 'input', 'output')

    def create(self, validated_data):
        question = self.context['question']
        if question.type != 'COD':
            raise QuestionTypeMismatch()
        return TestCase.objects.create(question=question, **validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    testcases = TestCaseSerializer(many=True, read_only=True)
    pk = serializers.IntegerField(read_only=True)
    tags = TagRelatedField(many=True, required=False)
    number_of_correct_choices = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = ('pk', 'title', 'description', 'type', 'choices', 'answers', 'testcases', 'extra',
                  'created_at', 'updated_at', 'tags', 'number_of_correct_choices')

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        question = Question.objects.create(**validated_data)
        for tag in tags:
            question.tags.add(tag)

        return question


    def update(self, instance, validated_data):
        validated_data.pop('choices', None)
        validated_data.pop('answers', None)
        validated_data.pop('testcases', None)
        tags = validated_data.pop('tags', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        instance.tags.set(tags)

        return instance


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('content',)

    def to_representation(self, instance):
        return instance.content

