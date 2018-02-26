from quizsys.apps.core.renderers import QuizsysJSONRenderer, QuizsysPaginationJSONRenderer


class UserJSONRenderer(QuizsysPaginationJSONRenderer):
    object_label = 'user'
    object_label_plural = 'users'
    count_label = 'usersCount'


class GroupJSONRenderer(QuizsysPaginationJSONRenderer):
    object_label = 'group'
    object_label_plural = 'groups'
    count_label = 'groupsCount'


class UserAllJSONRenderer(QuizsysJSONRenderer):
    object_label = 'user'
    object_label_plural = 'users'
