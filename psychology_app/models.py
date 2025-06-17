from django.db import models
from django.contrib.auth import get_user_model
from organizers.models import Organization, Partner, Customer

User = get_user_model()

class AnswerSet(models.Model):
    name = models.CharField(max_length=255)
    answers = models.JSONField(null=True)
    scores = models.JSONField(default=list)
    activate = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='answer_sets', null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='answer_sets', null=True, blank=True)
    class Meta:
        db_table = 'psychology_answerset'


class QuestionType(models.Model):
    symbol = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    activate = models.BooleanField(default=True)
    class Meta:
        db_table = 'psychology_question_type'


class SurveyType(models.Model):
    name = models.CharField(max_length=255)
    activate = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='survey_types', null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='survey_types', null=True, blank=True)
    class Meta:
        db_table = 'psychology_survey_type'


class Question(models.Model):
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    class Meta:
        db_table = 'psychology_question'


class Survey(models.Model):
    survey_type = models.ForeignKey(SurveyType, on_delete=models.CASCADE, related_name='surveys')
    answer_set = models.ForeignKey(AnswerSet, on_delete=models.CASCADE, related_name='surveys')
    title = models.CharField(max_length=255)
    description  = models.CharField(max_length=255, null=True, blank=True)
    evaluate = models.JSONField(null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='surveys', null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='surveys', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activate = models.BooleanField(default=True)
    class Meta:
        db_table = 'psychology_survey'


class SurveyQuestion(models.Model):
    survey = models.ForeignKey(Survey, on_delete = models.CASCADE, related_name = 'survey_questions')
    question = models.ForeignKey(Question, on_delete = models.CASCADE, related_name = 'survey_questions')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['survey', 'question'], name='unique_survey_question'
            )
        ]
        db_table = 'psychology_survey_question'


class PublishSurvey(models.Model):
    published_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    is_finished = models.BooleanField(default=False, blank=True)
    survey_details = models.JSONField()
    target = models.JSONField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='published_surveys', null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='published_surveys', null=True, blank=True)
    class Meta:
        db_table = 'psychology_publish_survey'


class PublishSurveyResult(models.Model):
    publish_survey = models.OneToOneField(PublishSurvey, on_delete=models.CASCADE, related_name='survey_result')
    result = models.JSONField(null=True)
    class Meta:
        db_table = 'psychology_publish_survey_result'


class UserPublishSurveyResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_publishsurvey_results')
    publish_survey = models.ForeignKey(PublishSurvey, on_delete=models.CASCADE, related_name='user_publishsurvey_results')
    response = models.JSONField(null=True)
    result = models.JSONField(null=True)
    finished_at = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='user_publishedsurveys_results', null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='user_publishedsurveys_results', null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'publish_survey'], name='unique_user_publishsurvey'
            )
        ]
        db_table = 'psychology_user_publish_survey_result'