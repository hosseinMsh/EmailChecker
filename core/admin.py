from django.contrib import admin
from .models import EmailConfiguration, EmailCheck

@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'sender_email', 'receiver_email', 'check_interval', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'sender_email', 'receiver_email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'is_active', 'check_interval')
        }),
        ('اطلاعات فرستنده', {
            'fields': ('sender_email', 'sender_password', 'smtp_server', 'smtp_port')
        }),
        ('اطلاعات گیرنده', {
            'fields': ('receiver_email', 'receiver_password', 'imap_server', 'imap_port')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmailCheck)
class EmailCheckAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'configuration', 'status', 'sent_at', 'received_at', 'delivery_time')
    list_filter = ('status', 'sent_at', 'received_at')
    search_fields = ('message_id', 'subject', 'error_message')
    readonly_fields = ('message_id', 'sent_at', 'received_at', 'delivery_time', 'created_at')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('configuration', 'message_id', 'subject', 'status')
        }),
        ('زمان‌بندی', {
            'fields': ('sent_at', 'received_at', 'delivery_time')
        }),
        ('خطاها', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
