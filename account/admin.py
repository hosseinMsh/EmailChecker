from django.contrib import admin
from account.models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_login_ip', 'last_login_time')
    search_fields = ('user__username', 'user__email', 'last_login_ip')
    readonly_fields = ('last_login_ip', 'last_login_time')
