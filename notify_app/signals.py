from django.core.cache import cache
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Notification
from .tasks import send_notification_task


@receiver(post_save, sender=Notification)
def send_notification_on_post_save(sender, instance, created, **kwargs): 
    if created: # IMMEDIATE NOTIFICATION
        if instance.send_time is None:
            send_notification_task.delay(instance.id)
            instance.sent = True
            instance.save()

    else: # SCHEDULE NOTIFICATION   
        if instance.send_time and instance.send_time <= timezone.now():
            send_notification_task.delay(instance.id)


@receiver(pre_delete, sender=Notification)
def clear_cache_on_pre_delete(sender, instance, **kwargs):
    user_ids = list(instance.users.values_list('user_id', flat=True))
    keys = [f'user_notifications_{uid}' for uid in user_ids]
    cache.delete_many(keys)