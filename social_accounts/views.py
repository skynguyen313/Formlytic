from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import GoogleSignInSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication
from core.ratelimit import rate_limit_decorator

@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuthAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowAny]
    @rate_limit_decorator(rate='10/m')
    def post(self, request):
        serializer = GoogleSignInSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            return Response(
                {'message': 'Authentication successful', 'user': user_data},
                status=status.HTTP_200_OK
            )
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
