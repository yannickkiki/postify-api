from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    class Meta:
        model = User
        fields = ['email', 'password', 'email_verified_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }
