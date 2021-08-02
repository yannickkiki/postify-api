from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from post.viewsets import PostViewSet
from user.viewsets import UserViewSet, EmailVerificationViewSet


router = routers.DefaultRouter()
router.register(r'post', PostViewSet, basename='post')
router.register(r'user', UserViewSet, basename='user')
router.register(r'user/email-verification', EmailVerificationViewSet, basename='email_verification')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
]
