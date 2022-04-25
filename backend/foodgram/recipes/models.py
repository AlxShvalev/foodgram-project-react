from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=200,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
        blank=True,
        null=True,
        help_text='Добавить изображение',
    )
    text = models.TextField(
        'Описание',
        help_text='Добавьте описание'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='Amount',
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
    )
    subscribers = models.ManyToManyField(
        User,
        related_name='favorites',
        blank=True,
    )
    buyers = models.ManyToManyField(
        User,
        related_name='shopping_cart',
        blank=True,
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
    )
    time_create = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )
    time_modify = models.DateTimeField(
        'Дата изменения',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-time_create',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Amount(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        'Количество',
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['recipe']
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.amount} {self.ingredient} в {self.recipe}'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=256,
        unique=True,
    )
    color = models.CharField(
        'Цветовой код',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']

    def __str__(self):
        return self.name
