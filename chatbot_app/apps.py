from django.apps import AppConfig


class ChatbotAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot_app'
    
    def ready(self):
        from .rag.chatbot import Chatbot
        self.chatbot = Chatbot()
        self.chatbot.setup_workflow()

        import chatbot_app.signals
