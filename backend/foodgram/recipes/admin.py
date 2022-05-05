from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Amount, Ingredient, Recipe, Tag


class IngredientResource(resources.ModelResource):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)


class AmountResource(resources.ModelResource):

    class Meta:
        model = Amount
        fields = ('id', 'recipe', 'ingredient', 'amount',)


class AmountAdmin(ImportExportModelAdmin):
    resource_class = AmountResource
    list_display = ('id', 'recipe', 'ingredient', 'amount',)


class RecipeResource(resources.ModelResource):
    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text', 'cooking_time', 'image')


class RecipeAdmin(ImportExportModelAdmin):
    resource_class = RecipeResource
    list_display = ('id', 'name', 'author', 'cooking_time', 'image')
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    filter_horizontal = ('subscribers', 'buyers', 'tags',)


class TagResource(resources.ModelResource):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class TagAdmin(ImportExportModelAdmin):
    resource_class = TagResource
    list_display = ('id', 'name', 'color', 'slug',)


admin.site.register(Amount, AmountAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
