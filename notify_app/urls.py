from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from .views import NotificationViewSet, UserNotificationViewSet, CustomerNotificationReadViewSet

router = DefaultRouter()
router.register(r'devices', FCMDeviceAuthorizedViewSet, basename='fcm_device')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'my-histories', UserNotificationViewSet, basename='user_notification')
router.register(r'customer-notification-read', CustomerNotificationReadViewSet, basename='customer_notification_read')

urlpatterns = [
    path('', include(router.urls)),
]
