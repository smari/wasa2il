import json
import requests

from datetime import datetime

from django.conf import settings
from django.db.models import Q

from polity.models import Polity

from gateway.exceptions import IcePirateException


def user_to_member_args(user):
    info = {
        'json_api_key': settings.ICEPIRATE['key'],

        'ssn': user.userprofile.verified_ssn,
        'name': user.userprofile.verified_name,
        'email': user.email,
        'username': user.username,
        'email_wanted': 'true' if user.userprofile.email_wanted else 'false',
        'added': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        'groups': [p.slug for p in user.polities.all()],
    }
    return info


def response_to_results(response):
    '''
    A unified way to deal with an IcePirate response.
    '''
    try:
        remote_data = json.loads(response.text)
    except ValueError:
        raise IcePirateException('JSON parsing error')

    member = remote_data['data'] if 'data' in remote_data else None
    error = remote_data['error'] if 'error' in remote_data else None
    return remote_data['success'], member, error


def add_member(user):

    data = user_to_member_args(user)

    try:
        response = requests.post('%s/member/api/add/' % settings.ICEPIRATE['url'], data=data)
    except:
        raise IcePirateException('Failed adding member to remote member registry')

    return response_to_results(response)


def update_member(user):

    data = user_to_member_args(user)

    try:
        response = requests.post(
            '%s/member/api/update/ssn/%s/' % (settings.ICEPIRATE['url'], user.userprofile.verified_ssn),
            data=data
        )
    except:
        raise IcePirateException('Failed updating member in remote member registry')

    return response_to_results(response)


def get_member(ssn):

    try:
        response = requests.post(
            '%s/member/api/get/ssn/%s/' % (settings.ICEPIRATE['url'], ssn),
            data={'json_api_key': settings.ICEPIRATE['key']}
        )
    except:
        raise IcePirateException('Failed getting member from remote member registry')

    return response_to_results(response)


def apply_member_locally(member, user):
    '''
    Takes an IcePirate member in the form of a dict and a regular local user
    and applies the data in the member to the local user.
    '''

    # Add user to polities according to remote user's groups, as well as
    # front polity, if one is designated.
    membership_polities = Polity.objects.filter(
        Q(slug__in=member['groups'].keys())
        | Q(is_front_polity=True)
    )
    for polity in membership_polities:
        polity.members.add(user)

    # Remove user from polities in which they are not a member.
    non_membership_polities = Polity.objects.exclude(
        Q(slug=None)
        | Q(slug='')
        | Q(slug__in=member['groups'].keys())
        | Q(is_front_polity=True)
    ).filter(members=user)
    for polity in non_membership_polities:
        polity.members.remove(user)
        polity.officers.remove(user)

    # Ask the member database if the user has consented to receiving
    # email and update user database accordingly.
    if user.userprofile.email_wanted != member['email_wanted']:
        user.userprofile.email_wanted = member['email_wanted']
        user.userprofile.save()

    # Ask the member database when the user registered, since this may impact
    # the user's right to vote.
    added = datetime.strptime(member['added'], '%Y-%m-%d %H:%M:%S')
    if user.userprofile.joined_org != added:
        user.userprofile.joined_org = added
        user.userprofile.save()
