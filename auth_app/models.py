from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_TYPES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    file = models.ImageField(upload_to="profiles/", default="", blank=True)
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=30, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=50, blank=True, default="")
    type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
