from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from .models import Notification, UserNotification
from .utils import send_firebase_notification
from core.utils import get_user_ids_from_target_notification

@shared_task
def check_appointment_notification():
    now = timezone.now()
    notifications = Notification.objects.filter(
        sent=False, 
        send_time__lte=now
    )
    
    for notification in notifications:
        notification.sent = True
        notification.save()

@shared_task
def send_notification_task(notification_id):
    try:
        instance = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return
    
    new_user_ids = get_user_ids_from_target_notification(instance)

    [cache.delete(f'user_notifications_{user_id}') for user_id in new_user_ids]

    if new_user_ids:
        UserNotification.objects.bulk_create([
            UserNotification(user_id=user_id, notification=instance) for user_id in new_user_ids
        ])
        
    send_firebase_notification(
        user_ids=list(new_user_ids),
        title=instance.title,
        body=instance.message
    )

