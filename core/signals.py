from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.dispatch import Signal

from core.models import UserProfile

from languagecontrol.utils import set_language


user_verified = Signal(providing_args=['user', 'request'])


@receiver(post_save, sender=User)
def ensure_userprofile(sender, instance, **kwargs):
    '''
    Make sure that a user profile always exists per user.
    '''
    UserProfile.objects.get_or_create(user_id=instance.id)


@receiver(user_logged_in)
def set_language_on_login(sender, user, request, **kwargs):
    set_language(request, user.userprofile.language)
