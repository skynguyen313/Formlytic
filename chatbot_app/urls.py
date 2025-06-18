from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QAViewSet, DocumentViewSet, FAQViewSet

router = DefaultRouter()
router.register(r'ask', QAViewSet, basename='ask')
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'faq', FAQViewSet, basename='faq')

urlpatterns = [
    path('', include(router.urls)),
]
