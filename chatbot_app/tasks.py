import logging
from django.core.exceptions import ObjectDoesNotExist
from .models import Document 
from .rag.vector_db import VectorDB
from .rag.file_loader import Loader


logger = logging.getLogger(__name__)


def add_document_task_thread(document_id: int, file_path: str):
    document = None

    try:
        document = Document.objects.get(id=document_id)
        
        if not file_path:
            raise ValueError('File path is empty.')

        docs = Loader().load(file_path=file_path)
        is_succeeded = VectorDB().add_data(new_documents=docs)

        if is_succeeded is None:
            raise RuntimeError('VectorDB returned None unexpectedly.')

        document.status = Document.Status.COMPLETED if is_succeeded else Document.Status.FAILED
        document.save(update_fields=['status'])

    except ObjectDoesNotExist:
        logger.error(f'Document with ID {document_id} not found.')
    except Exception as e:
        if document:
            document.status = Document.Status.FAILED
            document.save(update_fields=['status'])
        logger.exception(f'Error processing document {document_id}: {e}')
