from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import response, status, views, viewsets


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


class UserAPIViewSet(UserViewSet):
    pass


class UserSelfViewSet(viewsets.ModelViewSet):
    pass
