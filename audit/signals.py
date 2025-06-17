from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LogEntry
from student_app.models import Department, Major, Course, SchoolClass
from psychology_app.models import SurveyType, QuestionType, AnswerSet, Survey, PublishSurvey
from notify_app.models import Notification
from chatbot_app.models import FAQ, Document

from core.authentication import get_current_user

def log_create_update(sender, instance, created, **kwargs):
    user = get_current_user()
    if hasattr(instance, 'activate') and instance.activate is False:
        action = 'delete'
    else:
        action = 'create' if created else 'update'
    
    LogEntry.objects.create(
         user=user,
         model_name=sender.__name__,
         object_id=str(instance.pk),
         action=action
    )


models_to_log = [Department, Major, Course, SchoolClass,
                 SurveyType, QuestionType, AnswerSet, Survey, PublishSurvey,
                 Notification,
                 Document ,FAQ,
                 ]

for model in models_to_log:
    post_save.connect(log_create_update, sender=model, dispatch_uid=f"log_create_update_{model.__name__}")
