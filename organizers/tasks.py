from celery import shared_task
from accounts.utils import send_normal_email
from django.conf import settings
from .models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def send_organization_email(subject, body, to_email):
    email_data = {
        'email_subject': subject,
        'email_body': body,
        'to_email': to_email,
    }
    send_normal_email(email_data)

@shared_task
def create_customer_user_accounts(customer_emails):
    customers = Customer.objects.filter(email__in=customer_emails, user__isnull=True)
    for customer in customers:
        email = customer.email
        first_name = customer.first_name
        last_name = customer.last_name 
        user = User.objects.create_user(
            email=email,
            password=settings.DEFAULT_PASSWORD,
            first_name=first_name,
            last_name=last_name
        )
        customer.user = user
        customer.save(update_fields=['user'])

