import json
from datetime import datetime
import urllib

from django.conf import settings

from core.models import Polity, LocationCode

class IcePirateException(Exception):
    pass

def configure_external_member_db(user, create_if_missing=False):

    def add_user_to_front_polity():
        try:
            frontpolity = Polity.objects.get(is_front_polity=True)
            frontpolity.members.add(user)
        except Polity.DoesNotExist:
            pass

    url = settings.ICEPIRATE['url']
    key = settings.ICEPIRATE['key']

    request = urllib.urlopen('%s/member/api/get/ssn/%s?json_api_key=%s' % (url, user.userprofile.verified_ssn, key))
    content = request.read()
    remote_object = json.loads(content)
    print(remote_object)

    if remote_object['success']:
        add_user_to_front_polity()

        # Configure additional polities
        icepirate_groups = remote_object['data']['groups']

        for polity in Polity.objects.filter(slug__in = icepirate_groups):
            polity.members.add(user)

        for polity in Polity.objects.exclude(slug__isnull=True).exclude(slug__exact=''):
            if polity.is_member(user) and polity.slug not in icepirate_groups:
                polity.members.remove(user)
                polity.officers.remove(user)

        try:
            for prefix, location in (('pnr', 'legal_zip_code'),
                                     ('svfnr', 'legal_municipality_code')):
                user_legal_loc = remote_object['data'].get(location)
                if user_legal_loc:
                    loc_code = '%s:%s' % (prefix, user_legal_loc)
                    # Add user to location (zip code, county code) Polities
                    for polity in Polity.objects.filter(location_codes__in = LocationCode.objects.filter(location_code=loc_code)):
                        polity.members.add(user)

            # bre: DISABLED FOR NOW
            # remove user from other zip code polities
            #for polity in Polity.objects.exclude(zip_codes__isnull=True).exclude(zip_codes__in = ZipCode.objects.filter(zip_code=user_legal_zip_code)):
            #    if polity.is_member(user):
            #        polity.members.remove(user)
            #        polity.officers.remove(user)
        except:
            pass

        added = datetime.strptime(remote_object['data']['added'], '%Y-%m-%d %H:%M:%S')
        if not user.userprofile.joined_org or added < user.userprofile.joined_org:
            user.userprofile.joined_org = added
            user.userprofile.save()

    else:
        error = remote_object['error']

        if error == 'No such member':

            if create_if_missing:

                post_data = urllib.urlencode({
                    'ssn': user.userprofile.verified_ssn,
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

                add_user_to_front_polity()

            else:
                user.polities.clear()
                user.officers.clear()





