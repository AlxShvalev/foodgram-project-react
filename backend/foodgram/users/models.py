# from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.hashers import make_password
# from django.db import models
#
# from .managers import CustomUserManager
#
#
# class User(AbstractUser):
#     email = models.EmailField(unique=True, max_length=254)
#     first_name = models.CharField(
#         max_length=150,
#         blank=False,
#         verbose_name='Имя'
#     )
#     last_name = models.CharField(
#         max_length=150,
#         blank=False,
#         verbose_name='Фамилия'
#     )
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')
#
#     objects = CustomUserManager()
#
#     class Meta:
#         ordering = ('-username',)
#
#     def __str__(self):
#         return self.username
#
#     def get_full_name(self):
#         return self.first_name + self.last_name
#
#     def has_perm(self, perm, obj=None):
#         return True
#
#     def has_module_perms(self, app_label):
#         return True
#
#     def set_password(self, raw_password):
#         self.password = make_password(raw_password)
#         self._password = raw_password
