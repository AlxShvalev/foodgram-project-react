from django.contrib.auth import get_user_model
from rest_framework import serializers, validators

from .models import Follow
from recipes.models import Recipe


User = get_user_model()


class FavoriteSerializer(serializers.ModelSerializer):
    """Класс для сериализации рецепта в избранном"""
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, instance):
        return instance.image.url if instance.image else ''


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
