from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class EmailConfiguration(models.Model):
    """Configuration for email checking"""
    name = models.CharField(_('نام پیکربندی'), max_length=100)
    sender_email = models.EmailField(_('ایمیل فرستنده'))
    sender_password = models.CharField(_('رمز عبور فرستنده'), max_length=255)
    receiver_email = models.EmailField(_('ایمیل گیرنده'))
    receiver_password = models.CharField(_('رمز عبور گیرنده'), max_length=255)
    smtp_server = models.CharField(_('سرور SMTP'), max_length=100, default='smtp.gmail.com')
    smtp_port = models.IntegerField(_('پورت SMTP'), default=587)
    imap_server = models.CharField(_('سرور IMAP'), max_length=100, default='imap.gmail.com')
    imap_port = models.IntegerField(_('پورت IMAP'), default=993)
    check_interval = models.IntegerField(_('فاصله زمانی بررسی (دقیقه)'), default=10)
    is_active = models.BooleanField(_('فعال'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_configs')
    created_at = models.DateTimeField(_('زمان ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('زمان بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('پیکربندی ایمیل')
        verbose_name_plural = _('پیکربندی‌های ایمیل')

    def __str__(self):
        return f"{self.name} ({self.sender_email} -> {self.receiver_email})"


class EmailCheck(models.Model):
    """Record of an email check"""
    STATUS_CHOICES = (
        ('pending', _('در انتظار')),
        ('sent', _('ارسال شده')),
        ('received', _('دریافت شده')),
        ('failed', _('ناموفق')),
    )

    configuration = models.ForeignKey(EmailConfiguration, on_delete=models.CASCADE, related_name='checks')
    message_id = models.CharField(_('شناسه پیام'), max_length=255, unique=True)
    subject = models.CharField(_('موضوع'), max_length=255)
    status = models.CharField(_('وضعیت'), max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(_('زمان ارسال'), null=True, blank=True)
    received_at = models.DateTimeField(_('زمان دریافت'), null=True, blank=True)
    error_message = models.TextField(_('پیام خطا'), blank=True, null=True)
    delivery_time = models.DurationField(_('زمان تحویل'), null=True, blank=True)
    created_at = models.DateTimeField(_('زمان ایجاد'), auto_now_add=True)

    class Meta:
        verbose_name = _('بررسی ایمیل')
        verbose_name_plural = _('بررسی‌های ایمیل')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.message_id} - {self.status}"
