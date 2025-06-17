import json
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from .models import PublishSurvey, UserPublishSurveyResult, PublishSurveyResult
from core.utils import get_target_customers


@shared_task
def check_expiry_publish_survey():
    now = timezone.now()
    publish_surveys = PublishSurvey.objects.filter(
        is_finished=False,
        expired_at__lte=now
    )
    
    for publish_survey in publish_surveys:
        publish_survey.is_finished = True
        publish_survey.save()

@shared_task
def sync_publish_survey_users_task(survey_id, created):
    try:
        instance = PublishSurvey.objects.get(id=survey_id)
    except PublishSurvey.DoesNotExist:
        return

    target = instance.target

    if created:
        new_user_ids = list(get_target_customers(target, instance.organization, instance.partner).values_list('user_id', flat=True))
        participants = [
            UserPublishSurveyResult(user_id=user_id, publish_survey=instance, organization=instance.organization, partner=instance.partner)
            for user_id in new_user_ids
        ]

        cache.delete_many([f'published_survey_list_{user_id}' for user_id in new_user_ids])

        if participants:
            UserPublishSurveyResult.objects.bulk_create(participants)
    else:
        if instance.is_finished:
            cache_key = f'publish_survey_result_{instance.id}'
            cached_data = cache.get(cache_key)
            publish_survey_result, created_flag = PublishSurveyResult.objects.get_or_create(publish_survey=instance)

            if cached_data:
                data = json.loads(cached_data)
                publish_survey_result.result = data
                publish_survey_result.save()
                cache.delete(cache_key)

            old_user_ids = list(get_target_customers(target, instance.organization, instance.partner).values_list('user_id', flat=True))
            cache.delete_many([f'published_survey_list_{user_id}' for user_id in old_user_ids])
        else:
            new_user_ids = set(get_target_customers(target, instance.organization, instance.partner).values_list('user_id', flat=True))
            existing_qs = UserPublishSurveyResult.objects.filter(publish_survey=instance)
            existing_user_ids = set(existing_qs.values_list('user_id', flat=True))

            user_ids_to_remove = existing_user_ids - new_user_ids
            user_ids_to_add = new_user_ids - existing_user_ids

            if user_ids_to_remove:
                UserPublishSurveyResult.objects.filter(
                    publish_survey=instance, user_id__in=user_ids_to_remove
                ).delete()
                cache.delete_many([f'published_survey_list_{user_id}' for user_id in user_ids_to_remove])
            
            participants = [
                UserPublishSurveyResult(user_id=user_id, publish_survey=instance, organization=instance.organization, partner=instance.partner)
                for user_id in user_ids_to_add
            ]
            cache.delete_many([f'published_survey_list_{user_id}' for user_id in user_ids_to_add])

            if participants:
                UserPublishSurveyResult.objects.bulk_create(participants)