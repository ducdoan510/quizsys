from django.conf.urls import url

from .views import RegistrationAPIView, LoginAPIView, UserRetrieveUpdateDestroyAPIView, UserListAPIView, \
    GroupListCreateAPIView, GroupRetrieveUpdateDestroyAPIView, CurrentUserRetrieveAPIView, UserUploadAPIView

app_name = 'users'

urlpatterns = [
    url(r'^users/register/?$', RegistrationAPIView.as_view()),
    url(r'^users/?$', UserListAPIView.as_view()),
    url(r'^users/login/?$', LoginAPIView.as_view()),
    url(r'^user/(?P<username>[\w]+)/?$', UserRetrieveUpdateDestroyAPIView.as_view()),
    url(r'^user/retrieve/current/?$', CurrentUserRetrieveAPIView.as_view()),
    url(r'^user-upload/(?P<filename>[^/]+)/?$', UserUploadAPIView.as_view()),

    url(r'^groups/?$', GroupListCreateAPIView.as_view()),
    url(r'^group/(?P<group_name>\w+)/?$', GroupRetrieveUpdateDestroyAPIView.as_view())
]