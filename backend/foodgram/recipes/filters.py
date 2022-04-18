from django_filters.rest_framework import CharFilter, FilterSet

from .models import Ingredient


class IngredientNameFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
