from django.db import models
from django.contrib.auth import get_user_model
from organizers.models import Organization, Partner


User = get_user_model()

class Notification(models.Model):
    class NOTIFICATION(models.TextChoices):
        GENERAL = ('general', 'General')
        LEVEL_ALERT = ('level_alert', 'Level_Alert')
        TUITION_ALERT = ('tuition_alert', 'Tuition_Alert')
        NEW_SURVEY = ('new_survey', 'New_Survey')
        INCOMPLETED_SURVEY = ('incompleted_survey', 'Incompleted_Survey')
    category= models.CharField(max_length=20, choices=NOTIFICATION.choices, default = NOTIFICATION.GENERAL)
    title = models.CharField(max_length=255)
    message = models.TextField()
    target = models.JSONField()
    send_time = models.DateTimeField(null=True)
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name='notifications', null=True, blank=True)
    class Meta:
        db_table = 'notify_notification'


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='user_notifications')
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'notify_user_notification'