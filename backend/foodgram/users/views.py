from djoser.views import UserViewSet
from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .mixins import ListCreateDestroyModelViewSet
from .models import Follow
from .serializers import FollowSerializer
from api.paginators import NumPageLimitPagination


class UserAPIViewSet(UserViewSet):
    http_method_names = ('get', 'post')
    pagination_class = NumPageLimitPagination

    @action(methods=('get',),  detail=False,
            pagination_class=NumPageLimitPagination,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        following = Follow.objects.filter(user=user)
        print(following)
        data = []
        for obj in following:
            data.append(FollowSerializer(obj))
        return response.Response(data=data, status=status.HTTP_200_OK)


class FollowingViewSet(ListCreateDestroyModelViewSet):
    serializer_class = FollowSerializer
    pagination_class = NumPageLimitPagination
