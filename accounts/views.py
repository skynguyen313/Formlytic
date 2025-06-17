from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from accounts.models import OneTimePassword
from accounts.serializers import PasswordResetRequestSerializer,LogoutUserSerializer, UserRegisterSerializer, LoginSerializer, PasswordResetConfirmSerializer,ForgotPasswordSerializer, ForgotPasswordResetConfirmSerializer
from rest_framework import status
from .utils import send_generated_otp_to_email
from rest_framework.permissions import IsAuthenticated
from core.ratelimit import rate_limit_decorator


class RegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer
    
    @rate_limit_decorator(rate='5/m')
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data = user)
        if serializer.is_valid(raise_exception = True):
            serializer.save()
            user_data = serializer.data
            send_generated_otp_to_email(user_data['email'], request)
            return Response({
                'data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)



class VerifyUserEmail(GenericAPIView):
    @rate_limit_decorator(rate='5/m')
    def post(self, request):
        try:
            passcode  =  request.data.get('otp')
            user_pass_obj = OneTimePassword.objects.get(otp = passcode)
            user = user_pass_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message':'account email verified successfully'
                }, status = status.HTTP_200_OK)
            return Response({'message':'passcode is invalid user is already verified'}, status = status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as identifier:
            return Response({'message':'passcode not provided'}, status = status.HTTP_400_BAD_REQUEST)
        

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    @rate_limit_decorator(rate='5/m')
    def post(self, request):
        serializer =  self.serializer_class(data = request.data, context = {'request': request})
        serializer.is_valid(raise_exception = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    

class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    @rate_limit_decorator(rate='5/m')
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        return Response(status = status.HTTP_200_OK)

class ForgotPasswordResetConfirmView(GenericAPIView):
    serializer_class = ForgotPasswordResetConfirmSerializer
    @rate_limit_decorator(rate='5/m')
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        return Response(status = status.HTTP_200_OK)

class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    @rate_limit_decorator(rate='5/m')
    def post(self, request):
        serializer = self.serializer_class(data = request.data, context = {'request':request})
        serializer.is_valid(raise_exception = True)
        return Response(status = status.HTTP_200_OK)
    

class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    @rate_limit_decorator(rate='5/m')
    def post(self, request):
        serializer = self.serializer_class(data = request.data, context = {'request':request})
        serializer.is_valid(raise_exception = True)
        return Response(status = status.HTTP_200_OK)



class LogoutApiView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes  =  [IsAuthenticated]

    @rate_limit_decorator(rate='5/m')
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(status = status.HTTP_204_NO_CONTENT)
 