from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from .managers import UserManager
import string, random



class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length = 255, unique=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'accounts_user'

    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f'{self.last_name.title()} {self.first_name.title()}'



class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'accounts_onetimepassword'
    def __str__(self):
        return f'{self.user.first_name} - otp code'
    def is_valid(self):
        return timezone.now() - self.created_at < timedelta(minutes=5)
    
    @staticmethod
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))