from djoser.views import UserViewSet


class UserAPIViewSet(UserViewSet):
    http_method_names = ('get', 'post')
