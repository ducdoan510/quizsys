from quizsys.apps.core.renderers import QuizsysJSONRenderer, QuizsysPaginationJSONRenderer


class ChoiceJSONRenderer(QuizsysJSONRenderer):
    object_label = 'choice'
    object_label_plural = 'choices'


class AnswerJSONRenderer(QuizsysJSONRenderer):
    object_label = 'answer'
    object_label_plural = 'answers'


class TestCaseJSONRenderer(QuizsysJSONRenderer):
    object_label = 'testcase'
    object_label_plural = 'testcases'


class QuestionJSONRenderer(QuizsysPaginationJSONRenderer):
    object_label = 'question'
    object_label_plural = 'questions'
    count_label = 'questionsCount'


class TagJSONRenderer(QuizsysJSONRenderer):
    object_label = 'tag'
    object_label_plural = 'tags'


class QuestionAllJSONRenderer(QuizsysJSONRenderer):
    object_label = 'question'
    object_label_plural = 'questions'

