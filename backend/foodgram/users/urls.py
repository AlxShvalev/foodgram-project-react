from django.urls import include, path
from rest_framework import routers

from .views import UserAPIViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserAPIViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]