from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice 


def send_firebase_notification(user_ids, title, body):
    message = Message(
        notification=Notification(title=title, body=body)
    )

    devices = FCMDevice.objects.filter(user__id__in=user_ids)
    if devices:
        devices.send_message(message)