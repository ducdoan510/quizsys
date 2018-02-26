import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList


class QuizsysPaginationJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'object'
    object_label_plural = 'objects'
    count_label = 'count'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return None
        if data.get('results', None) is not None:
            return json.dumps({
                self.object_label_plural: data['results'],
                self.count_label: data['count']
            })
        elif data.get('errors', None) is not None:
            return super(QuizsysPaginationJSONRenderer, self).render(data)

        else:
            return json.dumps({
                self.object_label: data
            })


class QuizsysJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'object'
    object_label_plural = 'objects'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return None
        if isinstance(data, ReturnList):
            _data = json.loads(
                super(QuizsysJSONRenderer, self).render(data).decode('utf-8')
            )
            return json.dumps({
                self.object_label_plural: _data
            })
        elif data is not None:
            errors = data.get('errors', None)
            if errors is not None:
                return super(QuizsysJSONRenderer, self).render(data)

            return json.dumps({
                self.object_label: data
            })