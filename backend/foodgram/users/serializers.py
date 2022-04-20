from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Follow
from recipes.models import Recipe


User = get_user_model()


class FavoriteSerializer(serializers.ModelSerializer):
    """Класс для сериализации рецепта"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    """Класс для сериализации модели пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        )
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
        return user.is_authenticated and Follow.objects.filter(user=user, author=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

        def get_is_subscribed(self, obj):
            user = self.context['request'].user
            return user.is_authenticated and obj in user.follower.all()

        def get_recipes(self, obj):
            qs = obj.recipes.all()
            recipes_limit = self.context['request'].GET.get('recipe_limit')

            if recipes_limit:
                qs = qs[:recipes_limit]
            return FavoriteSerializer(instance=qs, many=True)

        def get_recipes_count(self,obj):
            return obj.recipes.all().count()
