import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .tasks import sync_publish_survey_users_task
from .models import PublishSurvey, UserPublishSurveyResult
from notify_app.models import Notification
from core.messages import NOTIFICATION_TITLES, NOTIFICATION_BODIES


@receiver(post_save, sender=PublishSurvey)
def add_notification_subscription(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            category=Notification.NOTIFICATION.NEW_SURVEY,
            title=NOTIFICATION_TITLES['survey'],
            message=NOTIFICATION_BODIES['survey'].format(instance.survey_details.get('title')),
            target=instance.target,
            organization=instance.organization,
            partner = instance.partner
        )


@receiver(post_save, sender=PublishSurvey)
def sync_on_post_save(sender, instance, created, **kwargs):
    sync_publish_survey_users_task.delay(instance.id, created)


@receiver(post_save, sender=UserPublishSurveyResult)
def accumulate_on_post_save(sender, instance, created, **kwargs):
    if not created:
        publish_survey_id = instance.publish_survey_id  
        cache_key = f'publish_survey_result_{publish_survey_id}'  

        cached_data = cache.get(cache_key)
        if cached_data is None:
            data = {}
        else:
            data = json.loads(cached_data)

        result = instance.result
        if result is not None:
            for category, severity in result.items():
                if category not in data:
                    data[category] = {
                        'Bình thường': 0,
                        'Nhẹ': 0,
                        'Trung bình': 0,
                        'Nặng': 0,
                        'Rất nặng': 0,
                    }

                data[category][severity] = data[category].get(severity, 0) + 1

            cache.set(cache_key, json.dumps(data), timeout=None)


# USER SUBMIT(UPDATE) PUBLSIH SURVEY RESULT
@receiver(post_save, sender=UserPublishSurveyResult)
def clear_cache_on_post_save(sender, instance, created, **kwargs):
    user_id = instance.user_id
    cache.delete(f'published_survey_list_{user_id}')
    if not created:
        cache.delete(f'user_{user_id}_publish_survey_result_list')
