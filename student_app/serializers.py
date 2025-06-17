from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    Department,
    Major,
    Course,
    SchoolClass,
    Student,
    Subject,
    Semester,
    StudentScore, 
    LevelAlert,
    TuitionAlert
    )


User = get_user_model()

class StudentLoginSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'password', 'full_name', 'access_token', 'refresh_token']

    def validate(self, attrs):
        student_id = attrs.get('id')
        password = attrs.get('password')
        request = self.context.get('request')

        try:
            student = Student.objects.get(id=student_id)
            email = student.email
        except Student.DoesNotExist:
            raise serializers.ValidationError('Student does not exist.')
        
        user = authenticate(request, email=email, password=password)

        if not user:
            raise serializers.ValidationError('Invalid login information.')

        if not user.is_active:
            raise serializers.ValidationError('Account has been locked.')
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        tokens = user.tokens()

        return {
            'email': user.email,
            'full_name': user.get_full_name,
            'access_token': str(tokens.get('access')),
            'refresh_token': str(tokens.get('refresh'))
        }


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

        extra_kwargs = {
            'name': {'validators': []},
        }

    def create(self, validated_data):
        name = validated_data.get('name')

        department = Department.objects.filter(name=name).first()
        if department:
            if department.activate:
                raise serializers.ValidationError({'name': ['department with name already exists.']})
            department.activate = True
            department.save()
            return department
        return super().create(validated_data)
    
class MajorSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = Major
        fields = ['id', 'name', 'department', 'department_name']
        extra_kwargs = {
            'name': {'validators': []},
        }
    
    def create(self, validated_data):
        name = validated_data.get('name')
        department = validated_data.get('department')

        major = Major.objects.filter(name=name, department=department).first()
        if major:
            if not major.activate:
                major.activate = True
                major.save()
                return major
            raise serializers.ValidationError({'non_field_errors': ['Major with this name and department already exists.']})
        return super().create(validated_data)

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_number', 'start_year']

    def create(self, validated_data):
        course_number = validated_data.get('course_number')
        start_year = validated_data.get('start_year')
        course = Course.objects.filter(course_number=course_number, start_year=start_year).first()
        if course:
            if not course.activate:
                course.activate = True
                course.save()
                return course
            raise serializers.ValidationError({
                'non_field_errors': ['Course with course_number and start_year already exists.']
            })
        return super().create(validated_data)


class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ['id', 'class_name', 'major', 'course']
        extra_kwargs = {
            'class_name': {'validators': []},
        }
    
    def create(self, validated_data):
        class_name = validated_data.get('class_name')
        major = validated_data.get('major')
        course = validated_data.get('course')
        
        school_class = SchoolClass.objects.filter(
            class_name=class_name,
            major=major,
            course=course
        ).first()
        
        if school_class:
            if not school_class.activate:
                school_class.activate = True
                school_class.save()
                return school_class
            raise serializers.ValidationError({
                'non_field_errors': ['SchoolClass with class_name, major and course already exists.']
            })
        
        return super().create(validated_data)


class StudentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    major_name = serializers.CharField(source='major.name', read_only=True)
    course_number = serializers.IntegerField(source='course.course_number', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'sex', 'dob', 'email',
                  'department', 'department_name',
                  'major', 'major_name',
                  'course', 'course_number',
                  'school_class', 'class_name',
        ]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'credit']

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'start_year', 'term']


class StudentScoreSerializer(serializers.ModelSerializer):
    student_info = StudentSerializer(source='student', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    semester_term = serializers.CharField(source='semester.term', read_only=True)
    semester_academic_year = serializers.CharField(source='semester.academic_year', read_only=True)
    class Meta:
        model = StudentScore
        fields = ['id',
                  'student', 'student_info',
                  'subject', 'subject_code', 'subject_name', 
                  'semester', 'semester_term', 'semester_academic_year',
                  'grading_formula', 'x', 'y', 'z', 'letter_grade']


class LevelAlertSerializer(serializers.ModelSerializer):
    student_info = StudentSerializer(source='student',read_only=True)
    class Meta:
        model = LevelAlert
        fields = ['id', 'student', 'student_info', 'semester', 'level']
        validators = []

class TuitionAlertSerializer(serializers.ModelSerializer):
    student_info = StudentSerializer(source='student',read_only=True)
    class Meta:
        model = TuitionAlert
        fields = ['id', 'student', 'student_info', 'semester', 'tuition']
        validators = []


class StudentDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    major_name = serializers.CharField(source='major.name', read_only=True)
    course_number = serializers.IntegerField(source='course.course_number', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    is_verified  = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    tuition = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'name', 'sex', 'dob', 'department_name', 'major_name', 'course_number', 'class_name', 'email', 'level', 'tuition', 'is_verified']

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs:
            user = kwargs.get('context', {}).get('user')
            if user and hasattr(user, 'student') and user.student:
                kwargs['instance'] = user.student
        super().__init__(*args, **kwargs)

    def get_level(self, obj):
        alert = obj.levelalerts.order_by('-semester__start_year', '-semester__term').first()
        return alert.level if alert else 0

    def get_tuition(self, obj):
        alert = obj.tuitionalerts.order_by('-semester__start_year', '-semester__term').first()
        return alert.tuition if alert else True

    def get_is_verified(self, obj):
        return bool(obj.user.is_verified)