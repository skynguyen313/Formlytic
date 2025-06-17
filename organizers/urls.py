from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import OrganizationRequestViewSet, OrganizationViewSet, PartnerViewSet, CustomerViewSet


router = DefaultRouter()
router.register(r'organization-requests', OrganizationRequestViewSet, basename='organization-request')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'partners', PartnerViewSet, basename='partner')
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = [
    path('', include(router.urls)),
]