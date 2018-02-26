from rest_framework.views import exception_handler

def core_exception_handler(exc, context):
    response = exception_handler(exc, context)
    handlers = {
        'NotFound': _handle_generic_error,
        'ValidationError': _handle_generic_error,
        'PermissionDenied': _handle_generic_error,
        'AuthenticationFailed': _handle_generic_error,
        'NotAuthenticated': _handle_generic_error,
        'MethodNotAllowed': _handle_generic_error,
        'NotAcceptable': _handle_generic_error,
        'UnsupportedMediaType': _handle_generic_error,
        'Throttled': _handle_generic_error,
    }
    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response


def _handle_generic_error(exc, context, response):
    response.data = {
        'errors': response.data
    }
    return response

# def _handle_not_found_error(exc, context, response):
#     view = context.get('view', None)
#
#     if view and hasattr(view, 'queryset') and view.queryset is not None:
#         error_key = view.queryset.model._meta.verbose_name
