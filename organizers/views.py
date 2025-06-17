from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from core.permissions import IsAdminUser, IsOrganizationUser, IsPartnerUser, IsCustomerUser
from core.pagination import CustomPagination
from .tasks import create_customer_user_accounts
from .models import OrganizationRequest, Organization, Partner, Customer
from .serializers import OrganizationRequestSerializer ,OrganizationSerializer, PartnerSerializer, CustomerSerializer

class OrganizationRequestViewSet(viewsets.ViewSet):
    pagination_class = CustomPagination
    serializer_class = OrganizationRequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        return OrganizationRequest.objects.all().order_by('-requested_at')
    
    def list(self, request):
        queryset = self.get_queryset()

        pending_param = request.query_params.get('pending', '').lower()
        approved_param = request.query_params.get('approved', '').lower()
        rejected_param = request.query_params.get('rejected', '').lower()

        filtered_queryset = queryset

        if pending_param in ['true', '1']:
            filtered_queryset = filtered_queryset.filter(status='pending')
        elif approved_param in ['true', '1']:
            filtered_queryset = filtered_queryset.filter(status='approved')
        elif rejected_param in ['true', '1']:
            filtered_queryset = filtered_queryset.filter(status='rejected')
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_queryset, request)
        serializer = self.serializer_class(page, many=True) 
        return paginator.get_paginated_response(serializer.data)
    
    def retrieve(self, request, pk=None):
        organization_request = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(organization_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, pk=None):
        organization_request = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(organization_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrganizationViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    serializer_class = OrganizationSerializer
    
    def get_queryset(self):
        return Organization.objects.all()

    def list(self, request):
        organizations = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(organizations, request)
        serializer = self.serializer_class(page, many=True) 
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        organization = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(organization)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, pk=None):
        organization = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(organization, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PartnerViewSet(viewsets.ViewSet):
    pagination_class = CustomPagination
    permission_classes = [IsOrganizationUser]
    serializer_class = PartnerSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization_profile'):
            return Partner.objects.filter(organization=user.organization_profile)
        return Partner.objects.none()

    def list(self, request):
        partners = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(partners, request)
        serializer = self.serializer_class(page, many=True) 
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        partner = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(partner)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        partner = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(partner, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        partner = get_object_or_404(self.get_queryset(), pk=pk)
        partner.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CustomerViewSet(viewsets.ViewSet):
    permission_classes = [IsPartnerUser]
    pagination_class = CustomPagination
    serializer_class = CustomerSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'partner_profile'):
            return Customer.objects.filter(partner=user.partner_profile)
        return Customer.objects.none()
    
    def list(self, request):
        customers = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(customers, request)
        serializer = self.serializer_class(page, many=True) 
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        user = request.user
        customers_data = request.data

        try:
            partner = user.partner_profile 
        except (Partner.DoesNotExist, AttributeError):
             return Response(
                {'error': 'Tài khoản của bạn không được liên kết với một Partner nào.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not isinstance(customers_data, list):
            return Response(
                {'error': 'Payload phải là một mảng (list) các đối tượng customer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incoming_emails = [item.get('email') for item in customers_data if item.get('email')]
        existing_emails = set(Customer.objects.filter(partner=partner, email__in=incoming_emails).values_list('email', flat=True))
        
        filtered_data = []
        seen_emails = set()
        for item in customers_data:
            email = item.get('email')
            if not email or email in existing_emails or email in seen_emails:
                continue
            
            seen_emails.add(email)
            filtered_data.append(item)

        if not filtered_data:
             return Response(
                {'message': 'Không có khách hàng mới nào để thêm. Dữ liệu có thể đã tồn tại hoặc bị trùng lặp.'},
                status=status.HTTP_200_OK
            )

        serializer = CustomerSerializer(data=filtered_data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        customers_to_create = []
        new_customers = [] 
        
        with transaction.atomic():
            for item_data in validated_data:
                customers_to_create.append(
                    Customer(
                        partner=partner,
                        email=item_data['email'],
                        extra_info=item_data.get('extra_info')
                    )
                )

            if customers_to_create:
                new_customers = Customer.objects.bulk_create(customers_to_create, ignore_conflicts=True)

        if new_customers:

            newly_created_emails = [customer.email for customer in new_customers]
            create_customer_user_accounts.delay(newly_created_emails)
            print(f"Triggering background task for emails: {newly_created_emails}")

            return Response(
                {'message': f'Đã tạo thành công {len(new_customers)} khách hàng mới cho partner.'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Yêu cầu đã được xử lý, nhưng không có khách hàng mới nào được thêm do tất cả đều đã tồn tại.'},
                status=status.HTTP_200_OK
            )

    @action(detail=False, methods=['get'], url_path='my-info', permission_classes=[IsCustomerUser])
    def my_info(self, request):
        user = request.user
        if hasattr(user, 'customer_profile'):
            customer = user.customer_profile
            serializer = self.serializer_class(customer)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        customer = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk=None):
        customer = get_object_or_404(self.get_queryset(), pk=pk)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    