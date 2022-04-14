from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import response, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from recipes.models import Ingredient, Recipe, Tag
from recipes.mixins import ListRetrieveModelViewSet
from recipes.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from users.serializers import UserSerializer

User = get_user_model()


class IngredientViewSet(ListRetrieveModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in ('GET',):
            return RecipeReadSerializer
        return RecipeWriteSerializer


class TagViewSet(ListRetrieveModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FavoriteViewSet(views.APIView):
    def post(self):
        recipe_id = self.kwargs.get('id')
        print(recipe_id)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.subscribers.add(recipe_id)
        serializer = FavoriteSerializer(recipe)
        return response.Response(data=serializer.data,
                                 status=status.HTTP_201_CREATED)


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     http_method_names = ('get', 'post')
#
#     @action(methods=['get'], detail=False,
#             permission_classes=[IsAuthenticated])
#     def me(self, request):
#         """Представление для эндпоинта 'текущий пользователь'."""
#         serializer = UserSerializer(self.request.user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     @action(methods=['post'], detail=False,
#             permission_classes=[IsAuthenticated])
#     def set_password(self, request):
#         """Представление для изменени пароля текущего пользователя"""
#         user = request.user
#         print(f'\n\n{request}\n\n')
#         serializer = SetPasswordSerializer(context=self.request['context'],
#                                            data=request.data)
#         print(f'\n\n{serializer}\n\n')
#         if serializer.is_valid(raise_exception=True):
#             new_password = serializer.data.get('new_password')
#             user.set_password(new_password)
#             user.save()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def get_permissions(self):
#         if self.action == 'create':
#             permission_classes = [AllowAny]
#         else:
#             permission_classes = [IsAuthenticated]
#
#         return [permission() for permission in permission_classes]

class UserAPIViewSet(UserViewSet):
    pass


class UserSelfViewSet(viewsets.ModelViewSet):
    pass
