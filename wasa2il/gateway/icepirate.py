import urllib
import json

from django.conf import settings

from core.models import Polity

def configure_polities_by_remote_groups(user):

    url = settings.ICEPIRATE['url']
    key = settings.ICEPIRATE['key']
    kennitala = user.userprofile.kennitala

    request = urllib.urlopen('%s/member/api/get/kennitala/%s?json_api_key=%s' % (url, kennitala, key))
    content = request.read()
    print content
    remote_object = json.loads(content)

    icepirate_groups = remote_object['data']['groups']

    for polity in Polity.objects.filter(slug__in = icepirate_groups):
        polity.members.add(user)

    for polity in Polity.objects.exclude(slug__isnull=True).exclude(slug__exact=''):
    	if polity.is_member(user) and polity.slug not in icepirate_groups:
    		polity.members.remove(user)

