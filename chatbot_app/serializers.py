from rest_framework import serializers
from .models import Document, FAQ, QAHistory
from django.contrib.auth import get_user_model

User = get_user_model()

class DocumentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'file_path', 'file_name', 'key', 'uploaded_at', 'author', 'status']

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
    student_id = serializers.IntegerField(read_only=True)
    key = serializers.CharField(read_only=True)
    question = serializers.CharField(required=True)
    thread_id = serializers.CharField(required=True)
    
    class Meta:
        model = User

    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student'):
            student = request.user.student
            attrs['key'] = f'K{student.course.course_number}'
            attrs['student_id'] = student.id
        else:
            raise serializers.ValidationError({'error': 'User has no Student information'})
        
        return attrs

class OutputQASerializer(serializers.Serializer):
    answer = serializers.CharField()

class StudentUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='student.id', read_only=True)
    name = serializers.CharField(source='student.name', read_only=True)
    email = serializers.CharField(source='student.email', read_only=True)
    
    course = serializers.IntegerField(source='student.course.id', read_only=True)
    course_number = serializers.CharField(source='student.course.course_number', read_only=True)
    
    department = serializers.IntegerField(source='student.department.id', read_only=True)
    department_name = serializers.CharField(source='student.department.name', read_only=True)
    
    major = serializers.IntegerField(source='student.major.id', read_only=True)
    major_name = serializers.CharField(source='student.major.name', read_only=True)
    
    school_class = serializers.IntegerField(source='student.school_class.id', read_only=True)
    class_name = serializers.CharField(source='student.school_class.class_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email',  
            'course', 'course_number',  
            'department', 'department_name',  
            'major', 'major_name',  
            'school_class', 'class_name'
        ]


class QAHistorySerializer(serializers.ModelSerializer):
    student = StudentUserSerializer(source='user', read_only=True)
    class Meta:
        model = QAHistory
        fields = ['student', 'created_at', 'thread_id', 'intent', 'question', 'answer']