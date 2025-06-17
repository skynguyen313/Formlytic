from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LogEntry(models.Model):
    ACTION_CHOICES = (
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
    )
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_log_entries')
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255) 
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logentry'

    def __str__(self):
        return f"{self.model_name} (ID: {self.object_id}) - {self.action} by {self.user} at {self.timestamp}"

