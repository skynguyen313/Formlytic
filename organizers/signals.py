from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import F
from django.utils import timezone
from .tasks import send_organization_email
from .models import OrganizationRequest, Organization
from django.contrib.auth import get_user_model
from .utils import generate_random_password, split_full_name

User = get_user_model()


@receiver(post_save, sender=OrganizationRequest)
def update_organization(sender, instance, created, **kwargs):
    if not created:
        if instance.status == 'approved':
            user, created = User.objects.get_or_create(
                email=instance.owner_email,
                defaults={
                    'first_name': '',
                    'last_name': '',
                    'is_organizer': True,
                    'is_partner': True,
                    'is_active': True,
                    'is_verified': True,
                })
            if created:
                random_password = generate_random_password()
                first_name, last_name = split_full_name(instance.owner_full_name)

                user.set_password(random_password)
                user.first_name = first_name
                user.last_name = last_name
                user.save() # Lưu lại để cập nhật mật khẩu đã băm và tên

                # Gửi email chứa mật khẩu tạm thời
                subject = 'Thông tin đăng ký quản trị viên tổ chức'
                body = (
                    f'Chào {instance.owner_full_name},\n\n'
                    f'Bạn đã trở thành quản trị viên của tổ chức {instance.organization_name}.\n'
                    f'Thông tin đăng nhập:\n'
                    f'  • Email (username): {instance.owner_email}\n'
                    f'  • Mật khẩu tạm thời: {random_password}\n\n'
                    f'Vui lòng đăng nhập và đổi mật khẩu ngay sau khi nhận được email này.\n'
                    f'Bạn có thể sử dụng tài khoản này để truy cập vào địa chỉ trang quản lý của bạn tại đây: https://www.vmu-sktt.io.vn/login/\n\n'
                    f'Cảm ơn bạn!'
                )
                send_organization_email.delay(subject, body, instance.owner_email)
            else:
                # Nếu người dùng đã tồn tại, chỉ gửi email thông báo
                subject = 'Thông báo vai trò mới'
                body = (
                    f'Chào {instance.owner_full_name},\n\n'
                    f'Bạn vừa được chỉ định làm quản trị viên của tổ chức {instance.organization_name}.\n'
                    f'Bạn có thể sử dụng tài khoản này để truy cập vào địa chỉ trang quản lý của bạn tại đây: https://www.vmu-sktt.io.vn/login/\n\n'
                    f'Cảm ơn bạn!'
                )
                send_organization_email.delay(subject, body, instance.owner_email)

            # Tạo Organization và liên kết với user
            org = Organization.objects.create(
                name=instance.organization_name,
                owner_full_name=instance.owner_full_name,
                email=instance.owner_email,
                owner=user
            )

            

           
            