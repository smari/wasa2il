import random
import string
import requests
import json
from wasa2il import settings

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from core.models import event_register, event_time_since_last
from core.models import User

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import issue
import election

def ssn_is_formatted_correctly(ssn):
    # We don't need any hard-core checksumming here, since we're only making
    # sure that the data format is correct, so that we can safely retrieve
    # parts of it through string manipulation.
    return ssn.isdigit() and len(ssn) == 10

def calculate_age_from_ssn(ssn):
    if not ssn_is_formatted_correctly(ssn):
        raise AttributeError('SSN must be numeric and exactly 10 digits long')

    # Determine year.
    century_num = ssn[9:]
    if century_num == '9':
        century = 1900
    elif century_num == '0':
        century = 2000
    else:
        raise AttributeError('%s is not a known number for any century' % century_num)
    year = century + int(ssn[4:6])

    # Determine month and day
    month = int(ssn[2:4])
    day = int(ssn[0:2])

    # Calculate the differences between birthdate and today.
    birthdate = datetime(year, month, day)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    age = relativedelta(today, birthdate).years

    return age

def is_ssn_human_or_institution(ssn):
    if not ssn_is_formatted_correctly(ssn):
        raise AttributeError('SSN must be numeric and exactly 10 digits long')

    return 'institution' if int(ssn[0:2]) > 31 else 'human'

def random_word(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


## Heartbeat command. Intended to be run either as a command
##   (see core.management.commands.heartbeat) or as a daemon thread.

def heartbeat():
    # Do all sorts of things that
    #   a) are due at this point in time.
    #   b) take a short amount of time to do.
    now = datetime.now()

    issue.heartbeat(now)
    election.heartbeat(now)
    event_register('heartbeat')

    # User review once per day max
    if event_time_since_last('core.utils', 'user_review') > timedelta(days=1):
        users = {
            'total_count': User.objects.count(),
            'verified_count': User.objects.filter(is_active=True).count(),
            'last30_count': User.objects.filter(last_login__gte=datetime.now()-timedelta(days=30)).count(),
            'last365_count': User.objects.filter(last_login__gte=datetime.now()-timedelta(days=365)).count(),
        }
        event_register('user_review', category='statistics', event=users)


## Push notifications tools

def push_server_post(action, payload):
    if not settings.FEATURES['push_notifications']:
        return False

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic %s" % settings.GCM_REST_API_KEY }
    req = requests.post("https://onesignal.com/api/v1/%s" % action, headers=header, data=json.dumps(payload))

    return req

def push_server_get(action, payload):
    if not settings.FEATURES['push_notifications']:
        return False

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic %s" % settings.GCM_REST_API_KEY }
    req = requests.get("https://onesignal.com/api/v1/%s" % action, headers=header, params=payload)

    return req

def push_send_notification(messages, segments, filters=None, buttons=None):
    payload = {"app_id": settings.GCM_APP_ID,
               "included_segments": segments,
               "contents": messages}

    # Example buttons:
    #
    # [{"id": "like-button", "text": "Like", "icon": "http://i.imgur.com/N8SN8ZS.png", "url": "https://yoursite.com"},
    # {"id": "read-more-button", "text": "Read more", "icon": "http://i.imgur.com/MIxJp1L.png", "url": "https://yoursite.com"}]
    #

    if buttons:
        payload['web_buttons'] = buttons

    if filters:
        payload['filters'] = filters
        payload.remove('included_segments')

    event_register('push_notification_sent', event=payload)
    return push_server_post('notifications', payload)

def push_send_notification_to_all_users(message, filters=None, buttons=None):
    # TODO: This needs to be updated to support i18n the way
    #       push_send_notification_to_polity_users does.
    #
    messages = {"en": message, "is": message}
    return push_send_notification(messages, ["All"], filters=filters, buttons=buttons)

def push_send_notification_to_polity_users(polity, message, msgargs=(), buttons=None):
    #   NOTE: Because it's hard to control user's language code as
    #         the push service understands it, we are instead using
    #         a tag named 'lang' to store the user's language preference.
    #         To accommodate translations, we send out push notifications
    #         to users in groups segmented by their 'lang' value, running
    #         each of these through i18n in the appropriate language.
    #
    old_lang = translations.get_language()

    for lang in ["is", "en"]:   # TODO: This should not be hard-coded.
        translation.activate(lang)
        messages = {"en": _(message) % msgargs}
        polityfilters = [
            {"field": "tag", "key": "lang", "relation": "=", "value": lang},
            {"operator": "and"},
            {"field": "tag", "key": "polity%d" % polity, "relation": "=", "value": "true"}
        ]
        return push_send_notification(messages, ["All"], polityfilters, buttons)

    translation.activate(old_lang)

def push_get_all_users():
    res = push_server_get('players', {"app_id": settings.GCM_APP_ID})
    if res.status_code == 200:
        return res.json()
    return False
