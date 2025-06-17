from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .utils import Google
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class GoogleSignInSerializer(serializers.Serializer):
    id_token = serializers.CharField()

    def validate(self, attrs):
        id_token = attrs.get('id_token')
        try:
            user_data = Google.validate(id_token)
        except Exception as e:
            raise serializers.ValidationError(f'Authentication failed: {str(e)}')
       
        email = user_data['email']

        if not any(email.endswith(domain) for domain in settings.ALLOWED_EMAIL_DOMAINS):
            raise serializers.ValidationError(f'Only emails with domains {settings.ALLOWED_EMAIL_DOMAINS} are allowed.')

        try:
            user = User.objects.get(email=email)
            return {
                'email': user.email,
                'tokens': user.tokens()
            }
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found. Please register first.')
