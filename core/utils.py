from django.db.models import Q
from notify_app.models import Notification
from organizers.models import Organization, Partner, Customer
from psychology_app.models import PublishSurvey, UserPublishSurveyResult


def get_target_customers(target: dict, organization: Organization = None, partner: Partner = None):
    if not organization and not partner:
        return Customer.objects.none()
    print(target)
    ownership_filter = Q()
    if organization:
        ownership_filter |= Q(partner__organization=organization)
    
    if partner:
        ownership_filter |= Q(partner=partner)

    filters = Q(user__isnull=False)

    customers_email = target.get('customers_email')
    if customers_email:
        filters &= Q(email__in=customers_email)

    sex = target.get('sex')
    if sex:
        if isinstance(sex, list):
            filters &= Q(extra_info__sex__in=sex)
        else:
            filters &= Q(extra_info__sex=sex)
            
    return Customer.objects.filter(ownership_filter & filters)


def get_incompleted_survey_user_ids(target: dict, organization: Organization = None, partner: Partner = None):
    publish_survey = PublishSurvey.objects.filter(id=target.get('publish_survey_id')).first()
    if publish_survey:
        user_ids = UserPublishSurveyResult.objects.filter(publish_survey=publish_survey, organization=organization, partner=partner,
                                                          response__isnull=True, result__isnull=True).values_list('user_id', flat=True)
        return user_ids
    return []


def get_user_ids_from_target_notification(instance: Notification):

    customer_qs = get_target_customers(instance.target, instance.organization, instance.partner)
    
    if instance.category == Notification.NOTIFICATION.INCOMPLETED_SURVEY:
        incompleted_survey_ids = get_incompleted_survey_user_ids(instance.target, instance.organization, instance.partner)
        customer_qs = customer_qs.filter(user_id__in=incompleted_survey_ids)
    
    return customer_qs.values_list('user_id', flat=True)



