from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for the Profile model.
    Displays the user, type, and creation date in the list view.
    """
    list_display = ("user", "type", "created_at")
    
admin.site.register(Profile, ProfileAdmin)