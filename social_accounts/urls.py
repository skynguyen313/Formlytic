from django.urls import path
from django.urls import path
from .views import GoogleAuthAPIView


urlpatterns = [
     path('google/', GoogleAuthAPIView.as_view(), name='google'),
]