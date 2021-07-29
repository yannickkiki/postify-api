from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from post.viewsets import PostViewSet
from user.viewsets import UserViewSet


router = routers.DefaultRouter()
router.register(r'post', PostViewSet)
router.register(r'user', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
]
