from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, ValidationError

User = get_user_model()


class UserSerializer(ModelSerializer):
    """Класс для сериализации модели пользователя"""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
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
            raise ValidationError(f'Пользователь с таким email уже существует')
        return email
