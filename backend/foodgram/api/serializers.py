from django.contrib.auth import get_user_model
from rest_framework import serializers, validators

from recipes.models import Amount, Ingredient, Recipe, Tag
from users.models import Follow


User = get_user_model()


class Base64Field(serializers.ImageField):
    """Класс для преобразования строки base64 в изображение."""

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
    """Сериализатор модели Tag"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class AmountReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода количества ингредиента в рецепте"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'amount', 'measurement_unit',)


class AmountWriteSerializer(serializers.Serializer):
    """Сериализатор для записи количества ингредиента в рецепт"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class UserSerializer(serializers.ModelSerializer):
    """Класс для сериализации модели пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password')
        extra_kwargs = {
            'email': {
                'required': True,
                'max_length': 254,
            },
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {
                'write_only': True,
                'max_length': 150,
            }
        }

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email'),
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return email

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                Follow.objects.filter(user=user, author=obj).exists())


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов"""
    ingredients = AmountReadSerializer(many=True, source='amount')
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('author',)

    def get_image(self, instance):
        return instance.image.url if instance.image else ''

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                obj in user.favorites.all())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                obj in user.shopping_cart.all())


class RecipeWriteSerializer(serializers.Serializer):
    """Сериализатор для записи/изменения рецепта"""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = AmountWriteSerializer(many=True)
    name = serializers.CharField(max_length=200)
    image = Base64Field(max_length=None, use_url=True)
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
        user = self.context['request'].user

        tags = validated_data.pop('tags')
        ingredients_field = validated_data.pop('ingredients')

        ingredients_list = []
        amounts = []

        recipe = Recipe(author=user, **validated_data)
        recipe.save()
        for obj in ingredients_field:
            ingredient = obj.get('id')
            if obj in ingredients_list:
                raise serializers.ValidationError(
                    {'error': 'Ингредиент уже добавлен в рецепт'}
                )
            amounts.append(
                Amount(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=obj.get('amount')
                )
            )
            ingredients_list.append(ingredient)

        Amount.objects.bulk_create(amounts)
        recipe.tags.set(tags)
        recipe.ingredients.set(ingredients_list)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        recipe.ingredients.clear()
        amount = Amount.objects.filter(recipe=recipe)
        amount.delete()

        tags = validated_data.pop('tags')
        ingredients_field = validated_data.pop('ingredients')
        ingredients_list = []
        amounts = []
        for obj in ingredients_field:
            ingredient = obj.get('id')
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    {'error': 'Ингредиент уже добавлен в рецепт'}
                )
            amounts.append(
                Amount(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=obj.get('amount')
                )
            )
            ingredients_list.append(ingredient)

        Amount.objects.bulk_create(amounts)

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
    """Класс для сериализации рецепта в избранном"""
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, instance):
        return instance.image.url if instance.image else ''


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на пользователя."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated and
            Follow.objects.filter(
                user=obj.user,
                author=obj.author
            ).exists()
        )

    def get_recipes(self, obj):
        params = self.context.get('request').query_params
        limit = params.get('recipes_limit')
        recipes = obj.author.recipes
        if limit:
            recipes = recipes.all()[:int(limit)]
        context = {'request': self.context.get('request')}
        return FavoriteSerializer(
            recipes, context=context, many=True).data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода всех подписок."""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author'],
                message='Вы уже подписаны на этого автора!'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        author = data['author']
        if request.user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionSerializer(instance, context=context).data
