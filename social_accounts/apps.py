from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
from config import settings

class SocialAccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_accounts'

    def ready(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
            firebase_admin.initialize_app(cred)
