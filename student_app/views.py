from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

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
from .serializers import (
    StudentLoginSerializer,
    DepartmentSerializer,
    MajorSerializer,
    CourseSerializer,
    SchoolClassSerializer,
    StudentSerializer,
    SubjectSerializer,
    SemesterSerializer,
    StudentScoreSerializer,
    StudentDetailSerializer, 
    LevelAlertSerializer, 
    TuitionAlertSerializer
)
from .tasks import create_student_accounts
from core.permissions import IsStaffUser, IsUser
from core.ratelimit import rate_limit_decorator
from core.pagination import CustomPagination

User = get_user_model()


class StudentLoginViewSet(viewsets.ViewSet):
    
    @rate_limit_decorator(rate='5/m')
    def create(self, request):
        serializer = StudentLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class DepartmentViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]

    @rate_limit_decorator(rate='50/m')
    def list(self, request):
        departments = Department.objects.filter(activate=True).order_by('-id')
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        department = get_object_or_404(Department, pk=pk, activate=True)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        department = get_object_or_404(Department, pk=pk)
        if department.activate:
            department.activate = False
            department.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MajorViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]

    @rate_limit_decorator(rate='50/m')
    def list(self, request):
        majors = Major.objects.filter(activate=True).order_by('-id')
        serializer = MajorSerializer(majors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = MajorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        major = get_object_or_404(Major, pk=pk, activate=True)
        serializer = MajorSerializer(major, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        major = get_object_or_404(Major, pk=pk)
        if major.activate:
            major.activate = False
            major.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]

    @rate_limit_decorator(rate='50/m')
    def list(self, request):
        courses = Course.objects.filter(activate=True).order_by('-id')
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk, activate=True)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        if course.activate:
            course.activate = False
            course.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SchoolClassViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]

    @rate_limit_decorator(rate='50/m')
    def list(self, request):
        school_classes = SchoolClass.objects.filter(activate=True).order_by('-id')
        serializer = SchoolClassSerializer(school_classes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = SchoolClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        school_class = get_object_or_404(SchoolClass, pk=pk, activate=True)
        serializer = SchoolClassSerializer(school_class, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        school_class = get_object_or_404(SchoolClass, pk=pk)
        if school_class.activate:
            school_class.activate = False
            school_class.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        student_id = request.query_params.get('student_id')
        course = request.query_params.get('course')
        department = request.query_params.get('department')
        major = request.query_params.get('major')
        school_class = request.query_params.get('school_class')

        filters = {}

        if student_id:
            filters['id'] = student_id
        else:
            if course:
                course_ids = course.split(',')
                filters['course_id__in'] = course_ids
            if department:
                department_ids = department.split(',')
                filters['department_id__in'] = department_ids
            if major:
                major_ids = major.split(',')
                filters['major_id__in'] = major_ids
            if school_class:
                school_class_ids = school_class.split(',')
                filters['school_class_id__in'] = school_class_ids

        students = Student.objects.filter(**filters).order_by('id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(students, request)
        serializer = StudentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    
    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        data = request.data

        course = data.get('course')
        department = data.get('department')
        major = data.get('major')
        school_class = data.get('school_class')
        students_data = data.get('students')

        if students_data is None or not isinstance(students_data, list):
            return Response(
                {'error': 'The students field must be a list.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not all([department, major, course, school_class]):
            return Response(
                {'error': 'Missing one or more of required fields: department, major, course, school_class.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for student in students_data:
            student.setdefault('department', department)
            student.setdefault('major', major)
            student.setdefault('course', course)
            student.setdefault('school_class', school_class)

        ids = [item.get('id') for item in students_data if item.get('id') is not None]
        existing_ids = {s.id for s in Student.objects.filter(id__in=ids)}
        filtered_data = []
        seen_ids = set()
        for item in students_data:
            student_id = item.get('id')
            if student_id:
                if student_id in existing_ids or student_id in seen_ids:
                    continue
                seen_ids.add(student_id)
            filtered_data.append(item)

        serializer = StudentSerializer(data=filtered_data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        with transaction.atomic():
            if validated_data:
                new_students = [Student(**{**item, 'user': None}) for item in validated_data]
                Student.objects.bulk_create(new_students, ignore_conflicts=True)

        new_student_ids = [item.get('id') for item in validated_data if item.get('id') is not None]
        if new_student_ids:
            create_student_accounts.delay(new_student_ids)

        return Response(status=status.HTTP_201_CREATED)
        

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentSerializer(student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        student = get_object_or_404(Student, id=pk)
        if student.user:
            student.user.delete()
        else:
            student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @rate_limit_decorator(rate='10/m')
    @action(detail=False, methods=['get'], permission_classes=[IsUser])
    def student_detail(self, request):
        user = request.user
        cache_key = f'student_detail_user_{user.id}'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            serializer = StudentDetailSerializer(context={'user': user})
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=3600)  # 1 hour
        return Response(cached_data, status=status.HTTP_200_OK)


class SubjectViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        
        search = request.query_params.get('search')

        subjects = Subject.objects.filter(activate=True).order_by('code')

        if search:
            subjects = subjects.filter(
                Q(code__icontains=search) | Q(name__icontains=search)
            )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subjects, request)
        serializer = SubjectSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = SubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        subject = get_object_or_404(Subject, pk=pk, activate=True)
        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        subject = get_object_or_404(Subject, pk=pk)
        if subject.activate:
            subject.activate = False
            subject.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SemesterViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        semesters = Semester.objects.filter(activate=True).order_by('-start_year', '-term')
        serializer = SemesterSerializer(semesters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = SemesterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        semester = get_object_or_404(Semester, pk=pk, activate=True)
        serializer = SemesterSerializer(semester, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        semester = get_object_or_404(Semester, pk=pk)
        if semester.activate:
            semester.activate = False
            semester.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentScoreViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        
        student_id = request.query_params.get('student_id')
        course = request.query_params.get('course')
        department = request.query_params.get('department')
        major = request.query_params.get('major')
        school_class = request.query_params.get('school_class')
        subject = request.query_params.get('subject')
        semester = request.query_params.get('semester')

        filters = {'student__isnull': False}

        if student_id:
            filters['student'] = student_id
        else:
            if course:
                course_ids = course.split(',')
                filters['student__course_id__in'] = course_ids
            if department:
                department_ids = department.split(',')
                filters['student__department_id__in'] = department_ids
            if major:
                major_ids = major.split(',')
                filters['student__major_id__in'] = major_ids
            if school_class:
                school_class_ids = school_class.split(',')
                filters['student__school_class_id__in'] = school_class_ids
            if subject:
                filters['subject'] = subject
            if semester:
                filters['semester'] = semester
        
        student_scores = StudentScore.objects.filter(**filters).order_by('id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(student_scores, request)
        serializer = StudentScoreSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        data = request.data
        subject_id = data.get('subject')
        semester_id = data.get('semester')
        student_scores_data = data.get('student_scores')

        if not subject_id or not semester_id or not student_scores_data:
            return Response(
                {'error': 'subject, semeter and student_scores are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(student_scores_data, list):
            return Response(
                {'error': 'student_scores must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in student_scores_data:
            item['subject'] = subject_id
            item['semester'] = semester_id

        serializer = StudentScoreSerializer(data=student_scores_data, many=True)
        serializer.is_valid(raise_exception=True)

        student_scores = [StudentScore(**item) for item in serializer.validated_data]
        StudentScore.objects.bulk_create(student_scores)

        return Response(status=status.HTTP_201_CREATED)
    
    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        student_score = get_object_or_404(StudentScore, pk=pk)
        serializer = StudentScoreSerializer(student_score, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @rate_limit_decorator(rate='20/m')
    def delete(self, request, pk=None):
        student_score = get_object_or_404(StudentScore, pk=pk)
        student_score.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LevelAlertViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        student_id = request.query_params.get('student_id')
        course = request.query_params.get('course')
        department = request.query_params.get('department')
        major = request.query_params.get('major')
        school_class = request.query_params.get('school_class')
        semester = request.query_params.get('semester')

        filters = {'student__isnull': False}

        if student_id:
            filters['student'] = student_id
        else:
            if course:
                course_ids = course.split(',')
                filters['student__course_id__in'] = course_ids
            if department:
                department_ids = department.split(',')
                filters['student__department_id__in'] = department_ids
            if major:
                major_ids = major.split(',')
                filters['student__major_id__in'] = major_ids
            if school_class:
                school_class_ids = school_class.split(',')
                filters['student__school_class_id__in'] = school_class_ids
            if semester:
                filters['semester'] = semester

        level_alerts = LevelAlert.objects.filter(**filters).order_by('id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(level_alerts, request)
        serializer = LevelAlertSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    
    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = LevelAlertSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        alerts = [LevelAlert(**item) for item in serializer.validated_data]
        LevelAlert.objects.bulk_create(alerts, ignore_conflicts=True)
        return Response(status=status.HTTP_201_CREATED)
    

    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        level_alert = get_object_or_404(LevelAlert, pk=pk)
        serializer = LevelAlertSerializer(level_alert, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        level_alert = get_object_or_404(LevelAlert, pk=pk)
        level_alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TuitionAlertViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        student_id = request.query_params.get('student_id')
        course = request.query_params.get('course')
        department = request.query_params.get('department')
        major = request.query_params.get('major')
        school_class = request.query_params.get('school_class')
        semester = request.query_params.get('semester')

        filters = {'student__isnull': False}

        if student_id:
            filters['student'] = student_id
        else:
            if course:
                course_ids = course.split(',')
                filters['student__course_id__in'] = course_ids
            if department:
                department_ids = department.split(',')
                filters['student__department_id__in'] = department_ids
            if major:
                major_ids = major.split(',')
                filters['student__major_id__in'] = major_ids
            if school_class:
                school_class_ids = school_class.split(',')
                filters['student__school_class_id__in'] = school_class_ids
            if semester:
                filters['semester'] = semester

        tuition_alerts = TuitionAlert.objects.filter(**filters).order_by('id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tuition_alerts, request)
        serializer = TuitionAlertSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    
    @rate_limit_decorator(rate='20/m')
    def create(self, request):
        serializer = TuitionAlertSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        alerts = [TuitionAlert(**item) for item in serializer.validated_data]
        TuitionAlert.objects.bulk_create(alerts, ignore_conflicts=True)
        return Response(status=status.HTTP_201_CREATED)
    
    @rate_limit_decorator(rate='20/m')
    def partial_update(self, request, pk=None):
        tuition_alert = get_object_or_404(TuitionAlert, pk=pk)
        serializer = TuitionAlertSerializer(tuition_alert, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @rate_limit_decorator(rate='20/m')
    def destroy(self, request, pk=None):
        tuition_alert = get_object_or_404(TuitionAlert, pk=pk)
        tuition_alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentVerificationStatsViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffUser]
    pagination_class = CustomPagination

    @rate_limit_decorator(rate='20/m')
    def list(self, request):
        is_verified = request.query_params.get('is_verified')
        student_id = request.query_params.get('student_id')
        course = request.query_params.get('course')
        department = request.query_params.get('department')
        major = request.query_params.get('major')
        school_class = request.query_params.get('school_class')

        filters = {}
        
        if is_verified is not None:
            is_verified = is_verified.lower() in ['true', '1']
           
        else:
            is_verified = False
            
        filters['user__is_verified'] = is_verified

        if student_id:
            filters['id'] = student_id
        else:
            if course:
                course_ids = course.split(',')
                filters['course_id__in'] = course_ids
            if department:
                department_ids = department.split(',')
                filters['department_id__in'] = department_ids
            if major:
                major_ids = major.split(',')
                filters['major_id__in'] = major_ids
            if school_class:
                school_class_ids = school_class.split(',')
                filters['school_class_id__in'] = school_class_ids

        total_students = Student.objects.count()
        total_verified_students = Student.objects.filter(user__is_verified=True).count()
        total_unverified_students = total_students - total_verified_students

        queryset = Student.objects.filter(**filters).order_by('id')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = StudentSerializer(page, many=True)
        data = {
            'students': serializer.data,
            'total_students': total_students,
            'total_verified_students': total_verified_students,
            'total_unverified_students': total_unverified_students
        }
        
        return paginator.get_paginated_response(data)
