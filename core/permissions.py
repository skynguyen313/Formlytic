from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Admin only
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsStaffUser(BasePermission):
    """
    Admin or Staff only
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
    
class IsUser(BasePermission):
    """
    User only
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
class IsOrganizationUser(BasePermission):
    """
    Organization user only
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.is_organizer and \
               request.user.organization_profile.activate

class IsPartnerUser(BasePermission):
    """
    Chỉ dành cho người dùng Partner.
    Cho phép truy cập nếu người dùng đã xác thực, là partner hoặc organizer,
    VÀ organization liên quan của họ (trực tiếp hoặc qua liên kết partner) đang active.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Đảm bảo đối tượng user có các cờ này, mặc định là False nếu không có
        is_partner = getattr(request.user, 'is_partner', False)
        is_organizer = getattr(request.user, 'is_organizer', False)

        if not (is_partner or is_organizer):
            return False

        # Kiểm tra trạng thái kích hoạt
        partner_org_is_active = False
        if is_partner:
            try:
                # request.user.partner_profile là đối tượng Partner
                # .organization là đối tượng Organization được liên kết
                # .activate là trường boolean trên Organization
                if request.user.partner_profile and request.user.partner_profile.organization:
                    partner_org_is_active = request.user.partner_profile.organization.activate
            except AttributeError:
                partner_org_is_active = False  # Profile hoặc organization liên kết có thể không tồn tại
        
        organizer_profile_is_active = False
        if is_organizer:
            try:
                # request.user.organization_profile là đối tượng Organization
                # .activate là trường boolean trên Organization
                if request.user.organization_profile:
                    organizer_profile_is_active = request.user.organization_profile.activate
            except AttributeError:
                organizer_profile_is_active = False # Profile có thể không tồn tại
        
        # Quyền truy cập được cấp nếu một trong hai trạng thái active liên quan là true
        return partner_org_is_active or organizer_profile_is_active


class IsCustomerUser(BasePermission):
    """
    Chỉ dành cho người dùng Customer.
    Cấp quyền truy cập nếu người dùng đã xác thực, là customer,
    và organization liên kết với partner của họ đang active.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        is_customer = getattr(request.user, 'is_customer', False)
        if not is_customer:
            return False
        
        try:
            # request.user.customer_profile là đối tượng Customer
            # .partner là đối tượng Partner được liên kết
            # .partner.organization là đối tượng Organization liên kết với Partner đó
            # .partner.organization.activate là trường boolean
            if request.user.customer_profile and \
               request.user.customer_profile.partner and \
               request.user.customer_profile.partner.organization:
                return request.user.customer_profile.partner.organization.activate
        except AttributeError:
            return False # Không thể duyệt qua chuỗi quan hệ
        
        return False # Mặc định từ chối nếu các kiểm tra ở trên không thành công