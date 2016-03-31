from django.conf import settings

def globals(request):

    ctx = {
        'INSTANCE_NAME': settings.INSTANCE_NAME,
        'INSTANCE_URL': settings.INSTANCE_URL.strip('/'),
        'INSTANCE_FACEBOOK_IMAGE': settings.INSTANCE_FACEBOOK_IMAGE,
    }

    return ctx
