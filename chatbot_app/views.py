import os
from django.core.cache import cache
from django.apps import apps
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Document, FAQ, QAHistory
from .serializers import (
    DocumentSerializer,
    FAQSerializer,
    InputQASerializer,
    OutputQASerializer,
)
from core.permissions import IsOrganizationUser, IsCustomerUser
from core.ratelimit import rate_limit_decorator
from core.pagination import CustomPagination

chatbot = apps.get_app_config('chatbot_app').chatbot


class QAViewSet(viewsets.ViewSet):
    permission_classes = [IsCustomerUser]

    @rate_limit_decorator(rate='5/m')
    def create(self, request):
        serializer = InputQASerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            question = serializer.validated_data['question']
            thread_id = serializer.validated_data['thread_id']
            user_id = request.user.id
            config = {'configurable': {'thread_id': thread_id, 'stream_mode': 'updates'}}
            current_intent, answer = chatbot.ask(question, config, user_id)

            QAHistory.objects.create(
                user = request.user,
                thread_id=thread_id,
                intent=current_intent,
                question=question,
                answer=answer,
            )

            output_serializer = OutputQASerializer(data={'answer': answer})
            if output_serializer.is_valid():
                return Response(output_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentViewSet(viewsets.ViewSet):
    permission_classes = [IsOrganizationUser]

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        documents = Document.objects.all().order_by('-uploaded_at')
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='30/m')
    def create(self, request):
        file = request.FILES.get('file')
        key = request.data.get('key')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DocumentSerializer(
            data={
                'file_path': file,
                'file_name': file.name,
                'key': key,
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        document = get_object_or_404(Document, pk=pk)
        document_file_path = document.file_path.path
        document.delete()
        if os.path.exists(document_file_path):
            try:
                os.remove(document_file_path)
            except Exception as e:
                print(f'Error deleting file: {e}')
        return Response(status=status.HTTP_204_NO_CONTENT)


class FAQViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsCustomerUser]
        else:
            permission_classes = [IsOrganizationUser]
        return [permission() for permission in permission_classes]

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        cache_key = 'faq_list'
        cache_data = cache.get(cache_key)
        if cache_data is None:
            faq_list = FAQ.objects.filter(activate=True).order_by('-created_at')
            serializer = FAQSerializer(faq_list, many=True)
            cache_data = serializer.data
            cache.set(cache_key, cache_data, timeout=86400)
        return Response(cache_data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = FAQSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.delete('faq_list')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        faq = get_object_or_404(FAQ, pk=pk)
        serializer = FAQSerializer(faq, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.delete('faq_list')
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        faq = get_object_or_404(FAQ, pk=pk)
        faq.activate = False
        faq.save()
        cache.delete('faq_list')
        return Response(status=status.HTTP_204_NO_CONTENT)
