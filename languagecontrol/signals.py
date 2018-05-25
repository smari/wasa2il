from django.contrib.auth.signals import user_logged_out
from django.conf import settings
from django.dispatch import receiver
from django.utils import translation

@receiver(user_logged_out)
def switch_to_default_language_on_logout(sender, user, request, **kwargs):
    # When logged out, we want to set the default language.
    if translation.LANGUAGE_SESSION_KEY in request.session:
        translation.activate(settings.LANGUAGE_CODE)
        del request.session[translation.LANGUAGE_SESSION_KEY]
