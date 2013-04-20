
from django.db.models import signals
from django.dispatch import receiver
from models import UserProfile
from django.contrib.admin.models import User


@receiver(signals.post_save, sender=User)
def create_userprofile(sender, instance, created, **kwargs):
    if created:
        pass
        # UserProfile.objects.create(user=instance)
