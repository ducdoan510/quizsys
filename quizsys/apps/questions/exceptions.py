from rest_framework import exceptions, status


class QuestionTypeMismatch(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Question type mismatch"


class QuestionPrimaryKeyMismatch(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Question primary key mismatch"
