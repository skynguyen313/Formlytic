from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
from config import settings

class NotifyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notify_app'

    def ready(self):
       import notify_app.signals
       if not firebase_admin._apps:
            cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
            firebase_admin.initialize_app(cred)
