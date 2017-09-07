from django.conf import settings


def globals(request):

    ctx = {
        'INSTANCE_NAME': settings.INSTANCE_NAME,
        'INSTANCE_URL': settings.INSTANCE_URL.strip('/'),
        'INSTANCE_FACEBOOK_IMAGE': settings.INSTANCE_FACEBOOK_IMAGE,
        'INSTANCE_FACEBOOK_APP_ID': settings.INSTANCE_FACEBOOK_APP_ID,
        'INSTANCE_VERSION': settings.WASA2IL_VERSION
    }

    return ctx
