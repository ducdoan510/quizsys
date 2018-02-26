from django.db import models

from quizsys.apps.core.models import TimestampedModel

QUESTION_TYPES = (
    ('MCQ', 'Multiple Choice Question'),
    ('FIB', 'Fill in Blank Question'),
    ('COD', 'Coding Question')
)


class Question(TimestampedModel):
    title = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField()
    type = models.CharField(choices=QUESTION_TYPES, max_length=255)
    extra = models.TextField(blank=True)
    tags = models.ManyToManyField('questions.Tag', related_name='questions')

    def __str__(self):
        return self.title

    @property
    def number_of_correct_choices(self):
        return self.choices.filter(is_correct_answer=True).count()


# choice of mcq questions
class Choice(TimestampedModel):
    content = models.TextField()
    is_correct_answer = models.BooleanField(default=False)
    question = models.ForeignKey('questions.Question', related_name='choices', on_delete=models.CASCADE)

    def __str__(self):
        return "%5s - %s" % (str(self.is_correct_answer), self.content)


# answer of fib question
class Answer(TimestampedModel):
    content = models.TextField()
    question = models.ForeignKey('questions.Question', related_name='answers', on_delete=models.CASCADE)

    def __str__(self):
        return self.content


# test cases of coding questions
class TestCase(TimestampedModel):
    input = models.TextField()
    output = models.TextField()
    question = models.ForeignKey('questions.Question', related_name='testcases', on_delete=models.CASCADE)

    def __str__(self):
        return "Input: %s\nOutput:%s" % (self.input, self.output)


# tags for classifying questions
class Tag(TimestampedModel):
    content = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.content



