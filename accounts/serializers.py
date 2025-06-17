from dataclasses import field
from .models import User, OneTimePassword
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import ValidationError
from .utils import send_normal_email


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        password=attrs.get('password', '')
        password2 =attrs.get('password2', '')
        if password !=password2:
            raise serializers.ValidationError('passwords do not match')
         
        return attrs

    def create(self, validated_data):
        user= User.objects.create_user(
            email = validated_data['email'],
            first_name = validated_data.get('first_name'),
            last_name = validated_data.get('last_name'),
            password = validated_data.get('password')
            )
        return user

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    role = serializers.CharField(max_length=50, read_only=True) 

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token', 'role']

    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')

        def get_user_role(user):
            if user.is_superuser:
                return 'admin'
            elif user.is_staff:
                return 'staff'
            elif user.is_organizer:
                return 'organizer'
            elif user.is_partner:
                return 'partner'
            else:
                return 'customer'
            
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed('invalid credential try again')
        if not user.is_active:
            raise AuthenticationFailed('User account locked')
        tokens = user.tokens()
        return {
            'email':user.email,
            'full_name':user.get_full_name,
            'role':get_user_role(user),
            'access_token':str(tokens.get('access')),
            'refresh_token':str(tokens.get('refresh'))
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Email does not exist.'))

        otp_code = OneTimePassword.generate_otp()
        otp_obj, created = OneTimePassword.objects.update_or_create(
            user=user, defaults={'otp': otp_code}
        )
        email_body = (
            f'Xin chào {user.first_name},\n\n'
            f'Mã OTP để đặt lại mật khẩu của bạn là: {otp_code}. '
            'Mã có hiệu lực trong 5 phút.'
        )
        data = {
            'email_body': email_body,
            'email_subject': 'Mã OTP đặt lại mật khẩu',
            'to_email': user.email
        }

        send_normal_email(data)
        return attrs

class ForgotPasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        fields = ['email', 'otp', 'new_password']

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Email does not exits.'))

        try:
            otp_obj = OneTimePassword.objects.get(user=user, otp=otp)
            if not otp_obj.is_valid():
                raise serializers.ValidationError(_('OTP code has expired.'))
        except OneTimePassword.DoesNotExist:
            raise serializers.ValidationError(_('Invalid OTP code.'))

        user.set_password(new_password)
        user.is_verified = True
        user.save()

        otp_obj.delete()

        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    class Meta:
        fields = []

    def validate(self, attrs):
        user = self.context['request'].user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError(_('Bạn cần đăng nhập để yêu cầu OTP.'))

        otp_code = OneTimePassword.generate_otp()
        otp_obj, created = OneTimePassword.objects.update_or_create(
            user=user, defaults={'otp': otp_code}
        )

        email_body = f'Xin chào {user.first_name},\n\nMã OTP để đặt lại mật khẩu của bạn là: {otp_code}. Mã có hiệu lực trong 5 phút.'
        data = {
            'email_body': email_body,
            'email_subject': 'Mã OTP đặt lại mật khẩu',
            'to_email': user.email
        }

        send_normal_email(data)

        return attrs

    
class PasswordResetConfirmSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        fields = ['otp', 'new_password']

    def validate(self, attrs):
        user = self.context['request'].user
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')

        if not user or not user.is_authenticated:
            raise serializers.ValidationError(_('You need to log in to change your password.'))

        try:
            otp_obj = OneTimePassword.objects.get(user=user, otp=otp)
            if not otp_obj.is_valid():
                raise serializers.ValidationError(_('OTP code has expired.'))
        except OneTimePassword.DoesNotExist:
            raise serializers.ValidationError(_('Invalid OTP code.'))

        user.set_password(new_password)
        user.is_verified = True
        user.save()

        otp_obj.delete()

        return attrs


    
class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is expired or invalid'
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise ValidationError(self.error_messages['bad_token'])