from django.core.mail import EmailMessage
import random
from django.conf import settings
from .models import User, OneTimePassword
from django.contrib.sites.shortcuts import get_current_site


def send_generated_otp_to_email(email, request): 
    subject = 'One time passcode for Email verification'
    otp = random.randint(100000, 999999) 
    current_site = get_current_site(request).domain
    user = User.objects.get(email=email)
    email_body = f'Hi {user.first_name} thanks for signing up on {current_site} please verify your email with the \n one time passcode {otp}'
    from_email = f'{settings.EMAIL_SENDER_NAME} <{settings.EMAIL_HOST_USER}>'
    otp_obj = OneTimePassword.objects.create(user=user, otp=otp) 
    d_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[user.email])
    d_email.send()


def send_normal_email(data):
    from_email = f'{settings.EMAIL_SENDER_NAME} <{settings.EMAIL_HOST_USER}>'
    email = EmailMessage(
        subject = data['email_subject'],
        body = data['email_body'],
        from_email = from_email,
        to = [data['to_email']]
    )
    email.send()