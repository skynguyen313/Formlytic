from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()

@receiver(post_save, sender=Student)
def update_email_user(sender, instance, created, **kwargs):
    if not created and instance.user:
        if instance.user.email != instance.email:
            instance.user.email = instance.email
            instance.user.save()