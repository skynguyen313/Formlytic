from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    AnswerSetViewSet, QuestionTypeViewSet, SurveyTypeViewSet,
    SurveyViewSet, QuestionViewSet, SurveyDetailViewSet, PublishSurveyViewSet,
    PublishedSurveyViewSet, UserPublishSurveyResultViewSet, UserSurveyCompletedViewSet, UserSurveyIncompletedViewSet,
    SurveyCustomerCountViewSet,
    PsychologyCustomerViewSet,
)

router = DefaultRouter()
router.register(r'answer-sets', AnswerSetViewSet, basename='answer_set')
router.register(r'question-types', QuestionTypeViewSet, basename='question_type')
router.register(r'survey-types', SurveyTypeViewSet, basename='survey_type')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'surveys', SurveyViewSet, basename='survey')
router.register(r'survey-detail', SurveyDetailViewSet, basename='survey_detail')
router.register(r'publish-surveys', PublishSurveyViewSet, basename='publish_survey')
router.register(r'published-surveys', PublishedSurveyViewSet, basename='published_survey')
router.register(r'user-survey-results', UserPublishSurveyResultViewSet, basename='user_publishsurvey_result')
router.register(r'user-survey-completed', UserSurveyCompletedViewSet, basename='user_survey_completed')
router.register(r'user-survey-incompleted', UserSurveyIncompletedViewSet, basename='user_survey_incompleted')
router.register(r'survey-customer-count', SurveyCustomerCountViewSet, basename='survey_customer_count')
router.register(r'psychology-customers', PsychologyCustomerViewSet, basename='psychology_student')

urlpatterns = [
    path('', include(router.urls)),
]
