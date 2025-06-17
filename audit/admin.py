from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from .models import LogEntry
from .mapping import MODEL_MAPPING, MODEL_NAME_MAPPING



class ActionFilter(SimpleListFilter):
    title = _("Hành động")
    parameter_name = "action"

    def lookups(self, request, model_admin):
        return LogEntry.ACTION_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(action=self.value())
        return queryset


class ModelNameFilter(SimpleListFilter):
    title = _("Tên mô hình")
    parameter_name = "model_name"

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.all().values_list('model_name', flat=True).distinct()
        return [(name, MODEL_NAME_MAPPING.get(name, name)) for name in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(model_name=self.value())
        return queryset

class UserFilter(SimpleListFilter):
    title = _("Người dùng")
    parameter_name = "user"

    def lookups(self, request, model_admin):
        qs = model_admin.model.objects.filter(user__isnull=False).values_list('user__id', 'user__email').distinct()
        return [(str(user_id), email) for user_id, email in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id=self.value())
        return queryset
    

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'get_model_name', 
        'get_object_id', 
        'action_display',
        'get_timestamp',
        'restore_link'
    )
    list_filter = (ActionFilter, ModelNameFilter, UserFilter)
    search_fields = ('model_name', 'user__email')
    ordering = ('-timestamp',)
    actions = ['restore_object']

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        model._meta.verbose_name = _("Nhật ký")
        model._meta.verbose_name_plural = _("Danh sách nhật ký")
    def get_model_name(self, obj):
        return MODEL_NAME_MAPPING.get(obj.model_name, obj.model_name)
    get_model_name.short_description = "Tên mô hình"

    def get_object_id(self, obj):
        return obj.object_id
    get_object_id.short_description = "Mã đối tượng"

    def action_display(self, obj):
        return obj.get_action_display()
    action_display.short_description = "Hành động"

    def get_timestamp(self, obj):
        return obj.timestamp
    get_timestamp.short_description = "Thời gian"

    def restore_link(self, obj):
        if obj.action == 'delete':
            model_cls = MODEL_MAPPING.get(obj.model_name)
            if model_cls:
                try:
                    instance = model_cls.objects.get(pk=obj.object_id)
                    if hasattr(instance, 'activate') and not instance.activate:
                        url = reverse('admin:audit_logentry_restore', args=[obj.pk])
                        return format_html('<a class="button" href="{}">Khôi phục</a>', url)
                except model_cls.DoesNotExist:
                    pass
        return ""
    restore_link.short_description = "Khôi phục"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'restore/<int:logentry_id>/',
                self.admin_site.admin_view(self.restore_view),
                name='audit_logentry_restore'
            ),
        ]
        return custom_urls + urls

    def restore_view(self, request, logentry_id, *args, **kwargs):
        log_entry = get_object_or_404(LogEntry, pk=logentry_id)
        model_cls = MODEL_MAPPING.get(log_entry.model_name)
        if not model_cls:
            self.message_user(request, "Unable to identify model for restoration.", messages.ERROR)
            return redirect("..")
        try:
            instance = model_cls.objects.get(pk=log_entry.object_id)
        except model_cls.DoesNotExist:
            self.message_user(request, "Record does not exist.", messages.ERROR)
            return redirect("..")

        if hasattr(instance, 'activate'):
            if not instance.activate:
                instance.activate = True
                instance.save()
                self.message_user(request, f"Restored: {instance}.", messages.SUCCESS)
            else:
                self.message_user(request, f"{instance} is already active.", messages.WARNING)
        else:
            self.message_user(request, f"Object {instance} does not have an 'activate' field.", messages.ERROR)
        return redirect("..")

    @admin.action(description="Restore selected objects")
    def restore_object(self, request, queryset):
        for log_entry in queryset:
            model_cls = MODEL_MAPPING.get(log_entry.model_name)
            if not model_cls:
                self.message_user(request, f"Cannot determine model for {log_entry.model_name}.", messages.ERROR)
                continue

            try:
                instance = model_cls.objects.get(pk=log_entry.object_id)
            except model_cls.DoesNotExist:
                self.message_user(request, f"Object with ID {log_entry.object_id} does not exist.", messages.ERROR)
                continue

            if hasattr(instance, 'activate'):
                if not instance.activate:
                    instance.activate = True
                    instance.save()
                    self.message_user(request, f"Restored: {instance}.", messages.SUCCESS)
                else:
                    self.message_user(request, f"{instance} is already active.", messages.WARNING)
            else:
                self.message_user(request, f"Object {instance} does not have an 'activate' field.", messages.ERROR)
