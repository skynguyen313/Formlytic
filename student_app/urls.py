from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    StudentLoginViewSet,
    DepartmentViewSet,
    MajorViewSet,
    CourseViewSet,
    SchoolClassViewSet,
    StudentViewSet,
    SubjectViewSet,
    SemesterViewSet,
    StudentScoreViewSet,
    LevelAlertViewSet,
    TuitionAlertViewSet,
    StudentVerificationStatsViewSet,
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'majors', MajorViewSet, basename='major')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'classes', SchoolClassViewSet, basename='schoolclass')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'semesters', SemesterViewSet, basename='semester')
router.register(r'scores', StudentScoreViewSet, basename='score')
router.register(r'level-alerts', LevelAlertViewSet, basename='levelalert')
router.register(r'tuition-alerts', TuitionAlertViewSet, basename='tuitionalert')
router.register(r'student-verification-stats', StudentVerificationStatsViewSet, basename='student_verification_stats')
urlpatterns = [
    path('login/', StudentLoginViewSet.as_view({'post': 'create'}), name='student-login'),
    path('', include(router.urls)),
]
