import logging
from concurrent.futures import ThreadPoolExecutor
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.apps import apps

from .models import Document
from .tasks import add_document_task_thread


logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=1)

@receiver(post_save, sender=Document)
def load_post_save_document(sender, instance, created, **kwargs):
    if created:
        if not instance.file_path:
            logger.error(f'Skipping document {instance.id}: No file path.')
            return
        transaction.on_commit(lambda: executor.submit(
            add_document_task_thread,
            instance.id,
            instance.file_path.path,
        ))
    else:
        chatbot = apps.get_app_config('chatbot_app').chatbot
        chatbot.reset()