from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import OrganizationRequest, Organization, Partner, Customer
from .utils import generate_random_password, split_full_name
from .tasks import send_organization_email
from django.contrib.auth import get_user_model

User = get_user_model()

class OrganizationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRequest
        fields = ['id', 'organization_name', 'owner_full_name', 'owner_email', 'notes', 'status', 'requested_at', 'reviewed_at']

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'owner_full_name', 'email', 'created_at', 'activate']

    def create(self, validated_data):
        email = validated_data.get('email')
        name = validated_data.get('name')
        owner_full_name = validated_data.get('owner_full_name')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': '',
                'last_name': '',
                'is_organizer': True,
                'is_partner': True,
                'is_active': True,
                'is_verified': True,
            }
        )

        # Chỉ thực hiện khi người dùng MỚI được tạo
        if created:
            random_password = generate_random_password()
            first_name, last_name = split_full_name(owner_full_name)

            user.set_password(random_password)
            user.first_name = first_name
            user.last_name = last_name
            user.save() # Lưu lại để cập nhật mật khẩu đã băm và tên

            # Gửi email chứa mật khẩu tạm thời
            subject = 'Thông tin đăng ký quản trị viên tổ chức'
            body = (
                f'Chào {owner_full_name},\n\n'
                f'Bạn đã trở thành quản trị viên của tổ chức {name}.\n'
                f'Thông tin đăng nhập:\n'
                f'  • Email (username): {email}\n'
                f'  • Mật khẩu tạm thời: {random_password}\n\n'
                f'Vui lòng đăng nhập và đổi mật khẩu ngay sau khi nhận được email này.\n'
                f'Bạn có thể sử dụng tài khoản này để truy cập vào địa chỉ trang quản lý của bạn tại đây: https://www.vmu-sktt.io.vn/login/\n\n'
                f'Cảm ơn bạn!'
            )
            send_organization_email.delay(subject, body, email)
        else:
            # Nếu người dùng đã tồn tại, chỉ gửi email thông báo
            subject = 'Thông báo vai trò mới'
            body = (
                f'Chào {owner_full_name},\n\n'
                f'Bạn vừa được chỉ định làm quản trị viên của tổ chức {name}.\n'
                f'Bạn có thể sử dụng tài khoản này để truy cập vào địa chỉ trang quản lý của bạn tại đây: https://www.vmu-sktt.io.vn/login/\n\n'
                f'Cảm ơn bạn!'
            )
            send_organization_email.delay(subject, body, email)

        # Tạo Organization và liên kết với user
        org = Organization.objects.create(
            name=name,
            owner_full_name=owner_full_name,
            email=email,
            owner=user
        )
        return org

class PartnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Partner
        # Thêm các trường mới vào fields
        fields = ['id', 'email', 'extra_info', 'created_at']

    def create(self, validated_data):
        # 1. Lấy thông tin người dùng (chủ sở hữu tổ chức) từ request
        organization_owner = self.context['request'].user

        # Kiểm tra xem người dùng có phải là chủ sở hữu tổ chức không
        try:
            organization = organization_owner.organization_profile
        except AttributeError:
            raise ValidationError("Người dùng hiện tại không phải là chủ sở hữu của bất kỳ Organization nào.")

        email = validated_data.get('email')
        name = validated_data.get('extra_info', {}).get('name', 'Partner Unknown')

        # 2. Kiểm tra xem đối tác đã tồn tại trong tổ chức này chưa
        if Partner.objects.filter(organization=organization, email=email).exists():
            raise ValidationError({"email": f"Đối tác với email '{email}' đã tồn tại trong tổ chức của bạn."})

        # 3. Lấy hoặc tạo mới người dùng (User)
        first_name, last_name = split_full_name(name)
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'is_partner': True,
                'is_active': True,
                'is_verified': True,
            }
        )

        # 4. Xử lý tùy theo người dùng là mới hay cũ
        if created:
            # Nếu người dùng MỚI được tạo -> tạo mật khẩu và gửi email chào mừng
            random_password = generate_random_password()
            user.set_password(random_password) # Mật khẩu được băm (hash) tự động
            user.save()

            subject = 'Thông tin đăng ký đối tác'
            body = (
                f'Chào bạn,\n\n'
                f'Bạn đã được mời làm đối tác của tổ chức {organization.name}.\n'
                f'Thông tin đăng nhập:\n'
                f'  • Email (username): {email}\n'
                f'  • Mật khẩu tạm thời: {random_password}\n\n'
                f'Vui lòng đăng nhập và đổi mật khẩu ngay sau khi nhận được email này.\n'
                f'Bạn có thể sử dụng tài khoản này để truy cập vào địa chỉ trang quản lý của bạn tại đây: https://www.vmu-sktt.io.vn/login/\n\n'
                f'Cảm ơn bạn!'
            )
        else:
            if not user.is_partner:
                user.is_partner = True
                user.save()

            subject = 'Thông báo vai trò đối tác mới'
            body = (
                f'Chào bạn,\n\n'
                f'Bạn vừa được thêm làm đối tác của tổ chức {organization.name}.\n'
                f'Bạn có thể sử dụng tài khoản này để truy cập vào địa chỉ trang quản lý của bạn tại đây: https://www.vmu-sktt.io.vn/login/\n\n'
                f'Cảm ơn bạn!'
            )
        
        # Gửi email bất đồng bộ
        send_organization_email.delay(subject, body, email)

        # 5. Tạo đối tượng Partner và liên kết với tổ chức và người dùng
        partner = Partner.objects.create(
            organization=organization,
            owner=user,
            **validated_data
        )
        return partner

    def update(self, instance, validated_data):
        # Logic update của bạn vẫn giữ nguyên, rất tốt.
        request_user = self.context['request'].user

        if instance.organization.owner != request_user:
            raise serializers.ValidationError("Bạn không có quyền chỉnh sửa Partner này.")

        # Cập nhật email cho cả User và Partner
        new_email = validated_data.get('email')
        if new_email and new_email != instance.email:
            if User.objects.filter(email=new_email).exclude(pk=instance.owner.pk).exists():
                raise serializers.ValidationError({"email": "Email này đã được sử dụng bởi User khác."})
            
            # Cập nhật đồng bộ email ở cả hai model
            instance.owner.email = new_email
            instance.email = new_email

        # Cập nhật thông tin khác
        instance.extra_info = validated_data.get('extra_info', instance.extra_info)

        instance.owner.save()
        instance.save()
        return instance


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['email', 'extra_info', 'joined_at']
