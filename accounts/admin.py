from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


class UserAdminCustom(UserAdmin):
    
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

        model._meta.verbose_name = _("Người dùng")
        model._meta.verbose_name_plural = _("Danh sách người dùng")

        model._meta.get_field('email').verbose_name = _("Địa chỉ Email")
        model._meta.get_field('first_name').verbose_name = _("Tên")
        model._meta.get_field('last_name').verbose_name = _("Họ")
        model._meta.get_field('is_staff').verbose_name = _("Nhân viên")
        model._meta.get_field('is_superuser').verbose_name = _("Quản trị viên")
        model._meta.get_field('is_organizer').verbose_name = _("Tổ chức")
        model._meta.get_field('is_partner').verbose_name = _("Đối tác")
        model._meta.get_field('is_verified').verbose_name = _("Đã xác thực")
        model._meta.get_field('is_active').verbose_name = _("Kích hoạt")
        model._meta.get_field('date_joined').verbose_name = _("Ngày tham gia")
        model._meta.get_field('last_login').verbose_name = _("Đăng nhập lần cuối")
        
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Thông tin cá nhân"), {"fields": ("first_name", "last_name")}),
        (
            _("Quyền hạn"),
            {
                "fields": (
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_organizer",
                    "is_partner",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Ngày quan trọng"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )
    list_display = ('email', 'last_name', 'first_name', 'is_superuser', 'is_staff', 'is_organizer', 'is_partner', 'is_verified', 'is_active', 'date_joined', 'last_login')
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)
    readonly_fields = ['date_joined', 'last_login']

admin.site.register(User, UserAdminCustom)
