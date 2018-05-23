from django.db.models.signals import post_save
from django.dispatch import receiver
from django.dispatch import Signal

from django.contrib.auth.models import User

from core.models import UserProfile


user_verified = Signal(providing_args=['user', 'request'])


@receiver(post_save, sender=User)
def ensure_userprofile(sender, instance, **kwargs):
    '''
    Make sure that a user profile always exists per user.
    '''
    UserProfile.objects.get_or_create(user_id=instance.id)
