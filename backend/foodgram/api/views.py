from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ValidationError

from .paginators import NumPageLimitPagination
from .permissions import IsAuthorOrReadOnly
from recipes.filters import IngredientNameFilter
from recipes.models import Ingredient, Recipe, Tag
from recipes.mixins import ListRetrieveModelViewSet
from recipes.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from users.serializers import FavoriteSerializer

User = get_user_model()


class IngredientViewSet(ListRetrieveModelViewSet):
    """Вьюсет для отображения списка ингредиентов и отдельного ингредиента"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientNameFilter


class TagViewSet(ListRetrieveModelViewSet):
    """Вьюсет для отображения списка тегов и отдельного тега"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения, запси, изменения и удаления рецептов."""
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = NumPageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags',)

    def get_queryset(self):
        if self.request.method == 'GET':
            is_favorited = self.request.GET.get('is_favorited', 0)
            in_cart = self.request.GET.get('is_in_shopping_cart', 0)
            user = self.request.user
            if user.is_authenticated:
                if is_favorited == '1':
                    return user.favorites.all()
                elif in_cart == '1':
                    return user.shopping_cart.all()
        return Recipe.objects.all()

    def get_permissions(self):
        if self.request.method in ('GET', 'PATCH', 'DELETE'):
            return (IsAuthorOrReadOnly(),)
        return (IsAuthenticated(),)

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

    @action(methods=('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        pass
