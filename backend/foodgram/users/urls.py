from django.urls import include, path
from rest_framework import routers

from api.views import UserAPIViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserAPIViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
