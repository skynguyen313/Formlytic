from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class OrganizationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Đã từ chối'),
    ]

    # Thông tin tổ chức được yêu cầu
    organization_name = models.CharField(max_length=255)
    owner_full_name = models.CharField(max_length=255)
    owner_email = models.EmailField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
        db_table = 'organizers_organization_request'
        

    def __str__(self):
        return f"{self.organization_name} ({self.get_status_display()})"


class Organization(models.Model):
    name = models.CharField(max_length=255)
    owner_full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organization_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    activate = models.BooleanField(default=True)
    class Meta:
        ordering = ['-created_at']
        db_table = 'organizers_organization'

class Partner(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='partners')
    email = models.EmailField(unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='partner_profile')
    extra_info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        db_table = 'organizers_partner'

class Customer(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='customers')
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    extra_info = models.JSONField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-joined_at']
        db_table = 'organizers_customer'

    @property
    def full_name(self):
        if self.extra_info and 'name' in self.extra_info:
            return self.extra_info.get('name', '')
        return ''

    @property
    def first_name(self):
        if not self.full_name:
            return ''
        return self.full_name.split(' ')[-1]

    @property
    def last_name(self):
        if not self.full_name:
            return ''
        parts = self.full_name.split(' ')
        return ' '.join(parts[:-1]) if len(parts) > 1 else ''

    def __str__(self):
        return self.full_name or self.email