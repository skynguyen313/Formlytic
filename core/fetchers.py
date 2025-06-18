from organizers.models import Organization, Partner, Customer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomerPsychologyFetcher:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_data(self):
        try:
            user = User.objects.get(pk=self.user_id)
        except User.DoesNotExist:
            return None
        
        survey_results = user.user_publishsurvey_results.order_by('-finished_at')[:3]
        result_data = []
        for survey in survey_results:
            publish_survey = survey.publish_survey
            result_data.append({
                'survey_title': publish_survey.survey_details.get('title'),
                'result': survey.result,
            })
        return result_data

class CustomerFetcher:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_data(self):
        try:
            user = User.objects.get(pk=self.user_id)
        except User.DoesNotExist:
            return None
        
        customer = customer.objects.get(user=user)
        return customer.extra_info
