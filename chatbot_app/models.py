from django.db import models
from .utils import CustomStorage
from django.contrib.auth import get_user_model

User = get_user_model()

class Document(models.Model):
    class Status(models.TextChoices):
        WAITING = ('waiting', 'Waiting')
        COMPLETED = ('completed', 'Completed')
        FAILED = ('failed', 'Failed')

    file_path = models.FileField(upload_to='documents/', storage=CustomStorage())
    file_name = models.CharField(max_length=255, null=False)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=False)
    author = models.CharField(max_length=255, null=False, blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.WAITING,
    )
    class Meta:
        db_table = 'chatbot_document'


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    activate = models.BooleanField(default=True)
    class Meta:
        db_table = 'chatbot_faq'

class QAHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qa_history')
    created_at = models.DateTimeField(auto_now_add=True)
    thread_id = models.CharField(max_length=36)
    intent = models.CharField(max_length=30)
    question = models.TextField()
    answer = models.TextField()

    class Meta:
        db_table = 'chatbot_qa_history'