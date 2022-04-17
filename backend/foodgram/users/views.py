from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination


class UserAPIViewSet(UserViewSet):
    http_method_names = ('get', 'post')
    pagination_class = PageNumberPagination

