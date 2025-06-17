from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Notification, UserNotification
from .serializers import NotificationSerializer, UserNotificationSerializer, NotificationReaderSerializer

from core.permissions import IsOrganizationUser, IsPartnerUser, IsCustomerUser
from core.ratelimit import rate_limit_decorator
from core.pagination import CustomPagination


class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            return Notification.objects.filter(partner=user.partner_profile)
        if hasattr(user, 'organization_profile') and user.organization_profile is not None:
            return Notification.objects.filter(organization=user.organization_profile)
        return Notification.objects.none()
    

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        notifications = self.get_queryset()
        
        category = request.query_params.get('category')
        sent = request.query_params.get('sent')
        search = request.query_params.get('search')
        if category:
            notifications = notifications.filter(category=category)
        if sent:
            sent_bool = sent.lower() in ['true', '1', 'yes']
            notifications = notifications.filter(sent=sent_bool)
        if search:
            notifications = notifications.filter(title__icontains=search)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = NotificationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = NotificationSerializer(notification, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserNotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsCustomerUser]

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        '''
        GET /user-notifications/
        '''
        cache_key = f'user_notifications_{request.user.id}'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            notifications = UserNotification.objects.filter(user=request.user).order_by('-id')[:30]
            serializer = UserNotificationSerializer(notifications, many=True)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=3600) # 1 hour
        return Response(cached_data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def retrieve(self, request, pk=None):
        '''
        GET /user-notifications/{pk}/
        '''
        notification = get_object_or_404(UserNotification, pk=pk, user=request.user)
        serializer = UserNotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        '''
        PATCH /user-notifications/{pk}/
        '''
        notification = get_object_or_404(UserNotification, pk=pk, user=request.user)
        serializer = UserNotificationSerializer(notification, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.delete(f'user_notifications_{request.user.id}')
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerNotificationReadViewSet(viewsets.ViewSet): 
    permission_classes = [IsPartnerUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def retrieve(self, request, pk=None):
        '''
        GET /customer-notification-read/{pk}/
        '''
        is_read = request.query_params.get('is_read')
        notification = get_object_or_404(Notification, pk=pk)
        filters = {'notification': notification, 'user__customer_profile__isnull': False}

        if is_read is not None:
            is_read = is_read.lower() in ['true', '1']
            filters['is_read'] = is_read
        else:
            is_read = False

        user_notifications = UserNotification.objects.filter(**filters).order_by('id')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(user_notifications, request)
        serializer = NotificationReaderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)





