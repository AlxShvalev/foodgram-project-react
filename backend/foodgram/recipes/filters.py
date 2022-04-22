from django_filters.rest_framework import (CharFilter, FilterSet,
                                           AllValuesMultipleFilter)

from .models import Ingredient, Recipe


class IngredientNameFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='exact',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)
