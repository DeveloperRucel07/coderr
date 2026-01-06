from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to create a Profile instance when a User is created.

    This function is triggered after a User instance is saved. If the User
    was newly created, it automatically creates a corresponding Profile
    instance linked to that User.

    Args:
        sender: The model class (User) that sent the signal.
        instance: The actual User instance being saved.
        created: A boolean indicating if the User was newly created.
        **kwargs: Additional keyword arguments from the signal.
    """
    if created:
        Profile.objects.create(user=instance)
