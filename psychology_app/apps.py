from django.apps import AppConfig

class PsychologyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'psychology_app'
    
    def ready(self):
        import psychology_app.signals