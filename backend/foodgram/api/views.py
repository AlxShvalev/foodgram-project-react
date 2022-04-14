from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import response, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
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

User = get_user_model()


class IngredientViewSet(ListRetrieveModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.request.method in ('GET',):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(methods=('post', 'delete'), detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if recipe in user.favorites.all():
                raise ValidationError('Рецепт уже в избранном')
            user.favorites.add(recipe)
            serializer = FavoriteSerializer(recipe)
            return response.Response(data=serializer.data,
                                     status=status.HTTP_201_CREATED)
        else:
            if recipe in user.favorites.all():
                user.favorites.remove(recipe)
                return response.Response(status=status.HTTP_204_NO_CONTENT)
            raise ValidationError('Такого рецепта нет в избранном')


class TagViewSet(ListRetrieveModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
