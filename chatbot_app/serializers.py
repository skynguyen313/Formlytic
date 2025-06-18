from rest_framework import serializers
from .models import Document, FAQ, QAHistory
from django.contrib.auth import get_user_model

User = get_user_model()

class DocumentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'file_path', 'file_name', 'uploaded_at', 'author', 'status']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user.get_full_name
        return super().create(validated_data)

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'created_at']


class InputQASerializer(serializers.Serializer):
    question = serializers.CharField(required=True)
    thread_id = serializers.CharField(required=True)
    class Meta:
        fields = ['question', 'thread_id']

class OutputQASerializer(serializers.Serializer):
    answer = serializers.CharField()
