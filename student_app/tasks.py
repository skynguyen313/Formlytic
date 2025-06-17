from celery import shared_task
from django.conf import settings
from .models import Student, User
from .utils import split_full_name

@shared_task
def create_student_accounts(student_ids):
    students = Student.objects.filter(id__in=student_ids, user__isnull=True)
    for student in students:
        email = student.email
        first_name, last_name = split_full_name(student.name)
        user = User.objects.create_user(
            email=email,
            password=settings.DEFAULT_PASSWORD,
            first_name=first_name,
            last_name=last_name
        )
        student.user = user
        student.save(update_fields=['user'])
