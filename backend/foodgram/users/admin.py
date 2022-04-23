from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow

User = get_user_model()


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')


class UserAdmin(BaseUserAdmin):
    list_display = ('pk', 'email', 'username', 'first_name', 'last_name',
                    'is_staff')
    list_filter = ('email', 'username')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
