import json
from datetime import datetime
import urllib

from django.conf import settings

from core.models import Polity

class IcePirateException(Exception):
    pass

def configure_external_member_db(user, create_if_missing=False):

    url = settings.ICEPIRATE['url']
    key = settings.ICEPIRATE['key']

    request = urllib.urlopen('%s/member/api/get/kennitala/%s?json_api_key=%s' % (url, user.userprofile.kennitala, key))
    content = request.read()
    remote_object = json.loads(content)

    if remote_object['success']:
        # Make sure that user is a part of front polity
        if settings.FRONT_POLITY != 0:
            user.polity_set.add(settings.FRONT_POLITY)

        # Configure additional polities
        icepirate_groups = remote_object['data']['groups']

        for polity in Polity.objects.filter(slug__in = icepirate_groups):
            polity.members.add(user)

        for polity in Polity.objects.exclude(slug__isnull=True).exclude(slug__exact=''):
            if polity.is_member(user) and polity.slug not in icepirate_groups:
                polity.members.remove(user)

        added = datetime.strptime(remote_object['data']['added'], '%Y-%m-%d %H:%M:%S')
        if not user.userprofile.joined_org or added < user.userprofile.joined_org:
            user.userprofile.joined_org = added
            user.userprofile.save()

    else:
        error = remote_object['error']

        if error == 'No such member':

            if create_if_missing:

                post_data = urllib.urlencode({
                    'kennitala': user.userprofile.kennitala,
                    'name': user.userprofile.verified_name,
                    'email': user.email,
                    'username': user.username,
                    'added': user.date_joined,
                })
                add_request = urllib.urlopen('%s/member/api/add/?json_api_key=%s&%s' % (url, key, post_data))
                content = add_request.read()
                remote_object = json.loads(content)

                if not remote_object['success']:
                    raise IcePirateException(remote_object['error'])

                # Make sure that user is a part of front polity
                if settings.FRONT_POLITY != 0:
                    user.polity_set.add(settings.FRONT_POLITY)

            else:
                user.polity_set.clear()





