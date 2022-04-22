from django_filters.rest_framework import BaseInFilter, CharFilter, FilterSet

from .models import Ingredient, Recipe


class CharFilterInFilter(BaseInFilter, CharFilter):
    pass


class IngredientNameFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = CharFilterInFilter(
        field_name='tags__slug',
        lookup_expr='in'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)
