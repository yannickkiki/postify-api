from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator as TokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.timezone import now

from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from user.models import User
from user.serializers import UserSerializer


class EmailVerificationViewSet(ViewSet):

    @action(methods=['post'], detail=False)
    def initiate(self, request, *args, **kwargs):
        data = request.data

        if 'verification_url' not in data:
            raise serializers.ValidationError("Missing parameter 'verification_url'")
        if 'email' not in data:
            raise serializers.ValidationError("Missing parameter 'email'")

        host = urlparse(data['verification_url']).netloc
        if host not in settings.ALLOWED_HOSTS:
            raise serializers.ValidationError(
                f"Invalid parameter 'verification_url': Host {host} not allowed"
            )

        user = User.objects.get(email=data['email'])

        verification_token = EmailVerificationTokenGenerator().make_token(user)
        uid_b64 = urlsafe_base64_encode(force_bytes(user.id))

        send_mail(
            subject="Email verification",
            recipient_email=user.email,
            content=f"Click this link to validate your email address: "
                    f"{data['verification_url']}?uid={uid_b64}&verification_token={verification_token}"
        )

        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def perform(self, request, *args, **kwargs):
        data = request.data

        if 'uid' not in data:
            raise serializers.ValidationError("Missing parameter 'uid'")
        if 'verification_token' not in data:
            raise serializers.ValidationError("Missing parameter 'verification_token'")

        uid_b64 = data['uid']
        user_id = urlsafe_base64_decode(uid_b64).decode()
        user = User.objects.get(id=user_id)
        is_token_valid = EmailVerificationTokenGenerator().check_token(
            user=user, token=data['verification_token']
        )
        if not is_token_valid:
            raise serializers.ValidationError('Invalid or expired verification_token.')

        user.email_verified_at = now()
        user.save(update_fields=['email_verified_at'])

        serializer = UserSerializer(instance=user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class EmailVerificationTokenGenerator(TokenGenerator):
    """
    Adaptation of Django's password reset logic
    (cf. django.contrib.auth.tokens.PasswordResetTokenGenerator)
    for one-time token generation to email verification process.
    The `email_verified_at` field is updated after email is successfully verified so
    the token will be invalidated after it's used.
    """

    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{user.email_verified_at}{timestamp}{user.email}'


def send_mail(subject, recipient_email, content):
    print(f"\n\n\n---------Email---------\n"
          f"Subject: {subject}\n"
          f"To: {recipient_email}\n"
          f"Content: {content}\n\n\n"
          )
    # todo: implement email sending
