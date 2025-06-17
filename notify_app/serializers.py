from rest_framework import serializers
from .models import Notification, UserNotification
from organizers.serializers import CustomerSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    sent = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'category', 'title', 'message', 'target', 'send_time', 'sent', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        if hasattr(user, 'partner_profile') and user.partner_profile is not None:
            partner_obj = user.partner_profile
            validated_data['partner'] = partner_obj
            validated_data['organization'] = partner_obj.organization

        # 2. Nếu user là owner của một Organization
        elif hasattr(user, 'organization_profile') and user.organization_profile is not None:
            org_obj = user.organization_profile
            validated_data['organization'] = org_obj

        else:
            raise serializers.ValidationError(
                "User này chưa được gán Organization hay Partner."
            )
        return super().create(validated_data)
    

class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'notification', 'is_read']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    
class NotificationReaderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(source='user.customer_profile', read_only=True)

    class Meta:
        model = UserNotification
        fields = ['customer']