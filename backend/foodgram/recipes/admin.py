from django.contrib import admin

from .models import Amount, Ingredient, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'


class AmountAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount',
    )


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'text',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )


admin.site.register(Amount, AmountAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
