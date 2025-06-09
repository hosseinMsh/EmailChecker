from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
