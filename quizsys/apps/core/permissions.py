from rest_framework import permissions, exceptions

from quizsys.apps.users.models import User


class IsStaffOrSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        lookup_url_kwarg = view.kwargs[view.lookup_url_kwarg]
        lookup_condition = {view.lookup_field: lookup_url_kwarg}
        try:
            requested_user = User.objects.get(**lookup_condition)
        except User.DoesNotExist:
            raise exceptions.NotFound("User does not exist")
        return request.user and (request.user == requested_user or request.user.is_staff)
