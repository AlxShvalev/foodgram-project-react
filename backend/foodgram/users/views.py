from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Follow
from .serializers import (FollowSerializer, SubscriptionSerializer,
                          UserSerializer)
from recipes.paginators import NumPageLimitPagination


User = get_user_model()


class UserAPIViewSet(UserViewSet):
    """Представление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = NumPageLimitPagination

    @action(methods=('get',), detail=False)
    def subscriptions(self, request, **kwargs):
        """Список подписок"""
        qs = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = SubscriptionSerializer(instance=page, many=True,
                                                context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return response.Response(serializer.data,
                                 status=status.HTTP_200_OK)

    @action(methods=('post',), detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        """Подписка на автора"""
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs['id'])
        data = {'user': user.id, 'author': author.id}
        serializer = FollowSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Удаляем подписку на автора"""
        author = get_object_or_404(User, id=self.kwargs['id'])
        subscription = request.user.follower.filter(author=author)
        if subscription.exists():
            subscription.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)

        return response.Response({'errors': 'Вы не подписаны на этого автора'},
                                 status=status.HTTP_400_BAD_REQUEST)
