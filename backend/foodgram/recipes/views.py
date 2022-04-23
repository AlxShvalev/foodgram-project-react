from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from .paginators import NumPageLimitPagination
from .permissions import IsAuthorOrReadOnly
from recipes.filters import IngredientNameFilter, RecipeFilter
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
    """Представление для отображения списка ингредиентов и ингредиента"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientNameFilter


class TagViewSet(ListRetrieveModelViewSet):
    """Представление для отображения списка тегов и тега"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для отображения, запси, изменения и удаления рецептов"""
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = NumPageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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

    @action(methods=('post',), detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        """Добавить рецепт в избранное"""
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        user = request.user
        if recipe in user.favorites.all():
            return response.Response({'error': 'Рецепт уже в избранном'},
                                     status=status.HTTP_400_BAD_REQUEST)
        user.favorites.add(recipe)
        serializer = FavoriteSerializer(recipe)
        return response.Response(data=serializer.data,
                                 status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        """Удаляем рецепт из избранного"""
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        user = request.user
        if recipe in user.favorites.all():
            user.favorites.remove(recipe)
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response({'error': 'Такого рецепта нет в избранном'},
                                 status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('post',), detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        """Добавить рецепт в корзину"""
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        user = request.user
        if recipe in user.shopping_cart.all():
            return response.Response({'error': 'Рецепт уже в корзине'},
                                     status=status.HTTP_400_BAD_REQUEST)
        user.shopping_cart.add(recipe)
        serializer = FavoriteSerializer(recipe)
        return response.Response(data=serializer.data,
                                 status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        """Удаляем рецепт из корзины"""
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        user = request.user
        if recipe in user.shopping_cart.all():
            user.shopping_cart.remove(recipe)
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response({'error': 'Такого рецепта нет в корзине'},
                                 status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('get',), detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        shopping_cart = request.user.shopping_cart.all()
        ingredients_list = {}
        for recipe in shopping_cart:
            for amount in recipe.amount.all():
                ingredient = amount.ingredient.__str__()
                if ingredient in ingredients_list:
                    ingredients_list[ingredient] += int(amount.amount)
                else:
                    ingredients_list[ingredient] = int(amount.amount)
        print(ingredients_list)

        return response.Response(status=status.HTTP_200_OK)
