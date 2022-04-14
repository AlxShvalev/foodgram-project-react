from rest_framework import serializers

from recipes.models import Amount, Ingredient, Recipe, Tag
from users.serializers import UserSerializer


class Base64Field(serializers.ImageField):

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complited_file_name = '%s.%s' % (file_name, file_extension,)
            data = ContentFile(decoded_file, name=complited_file_name)

        return super(Base64Field, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = 'jpg' if extension == 'jpeg' else extension
        return extension


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class AmountReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'amount', 'measurement_unit',)


class AmountWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def validate_id(self, data):
        if Ingredient.objects.filter(pk=data).exists():
            return data
        raise serializers.ValidationError(f'Ингредиент c id={data} не найден')


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = AmountReadSerializer(many=True, source='amount')
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                user.favorites.filter(pk=obj.pk).exists())


class RecipeWriteSerializer(serializers.Serializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = AmountWriteSerializer(many=True)
    name = serializers.CharField(max_length=200)
    image = Base64Field(max_length=None, use_url=True)
    text = serializers.CharField()
    cooking_time = serializers.IntegerField()

    def create(self, validated_data):
        user = self.context['request'].user

        tags = validated_data.pop('tags')

        ingredients_field = validated_data.pop('ingredients')
        ingredients_list = []
        ingredients_data = []
        recipe = Recipe(author=user, **validated_data)
        recipe.save()
        for obj in ingredients_field:
            ingredient = Ingredient.objects.get(pk=obj['id'])
            ingredients_data.append(
                Amount(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=obj.get('amount')
                )
            )
            ingredients_list.append(ingredient)

        amounts = Amount.objects.bulk_create(ingredients_data)
        recipe.tags.add(*tags)
        recipe.ingredients.add(*ingredients_list)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        recipe.ingredients.clear()
        amount = Amount.objects.filter(recipe=recipe)
        amount.delete()
        tags = validated_data.pop('tags')
        ingredients_field = validated_data.pop('ingredients')
        ingredients_list = []
        ingredients_data = []
        for obj in ingredients_field:
            ingredient = Ingredient.objects.get(pk=obj['id'])
            ingredients_data.append(
                Amount(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=obj.get('amount')
                )
            )
            ingredients_list.append(ingredient)

        amounts = Amount.objects.bulk_create(ingredients_data)

        recipe.name = validated_data.get('name', recipe.name)
        recipe.image = validated_data.get('image', recipe.image)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)

        recipe.save()
        recipe.tags.add(*tags)
        recipe.ingredients.add(*ingredients_list)

        return recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
