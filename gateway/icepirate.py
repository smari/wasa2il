import json
import random
import requests
from datetime import datetime

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse as django_url
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import slugify


from core.models import UserProfile

from polity.models import Polity


class IcePirateException(Exception):
    pass


def _password_reset_url(user):
    # This acts as if the users had submitted the password reset form,
    # giving us the URL+token needed to change the password.
    iu = settings.INSTANCE_URL
    if iu.endswith('/'):
        iu = iu[:-1]
    return iu + django_url(
        'auth_password_reset_confirm', None, None, {
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)})


def _icepirate_user_data(user):
    info = {
        'json_api_key': settings.ICEPIRATE['key'],
        'ssn': user.userprofile.verified_ssn,
        'name': user.userprofile.verified_name,
        'email': user.email,
        'username': user.username,
        'added': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return info

def _make_username(name, email):
    # This will create a username that isn't completely useless, but is
    # still somewhat anonymousish.
    for tries in range(1, 100):
        try:
            fn = name.split()[0].lower()
        except:
            try:
                fn = email.split('@')[0].lower()
            except:
                fn = 'anon'
        username = '%s_%s' % (slugify(fn), random.randint(13, tries*100))
        if not User.objects.filter(username=username).exists():
            return username
    raise ValueError('Could not create username from %s/%s' % (name, email))


@transaction.atomic
def adduser(request, ssn=None, name=None, email=None, added=None, username=None):
    if ssn is None:
        assert(request.GET.get('key') == settings.ICEPIRATE['key'])

    # Parse args...
    ssn = ssn or request.GET.get('ssn')
    name = name or request.GET.get('name')
    email = email or request.GET.get('email')
    added = added or request.GET.get('added')
    username = username or request.GET.get('username')
    if added:
        added = datetime.strptime(added, '%Y-%m-%d %H:%M:%S')
    else:
        added = timezone.now()

    # Look up all the users that match
    users = []
    if ssn:
        users.extend(User.objects.filter(userprofile__verified_ssn=ssn))
    if username:
        users.extend(User.objects.filter(username=username))
    if email:
        users.extend(User.objects.filter(email=email))

    # Update or create user
    try:
        user = users[0]
        # Sanity checks...
        assert(len([u for u in users if u != user]) == 0)
        if user.userprofile.verified_ssn:
            assert(user.userprofile.verified_ssn == ssn)
        else:
            # User exist, is not verified! Just update SSN.
            user.userprofile.verified_ssn = ssn
            user.userprofile.save()
    except IndexError:
        # User does not exist. Create user, yay!
        if not username:
            username = _make_username(name, email)
        user = User(username=username, email=email)
        user.save()
        prof = UserProfile(user=user, verified_ssn=ssn, joined_org=added)
        prof.save()

    response_data = _icepirate_user_data(user)
    response_data.update({
        'reset_url': _password_reset_url(user),
        'success': True})

    return HttpResponse(
        json.dumps(response_data), content_type='application/json')


def configure_external_member_db(user, create_if_missing=False):
    # No point hitting the API if we don't have an SSN to update
    if not user.userprofile.verified_ssn:
        return

    def add_user_to_front_polity():
        try:
            frontpolity = Polity.objects.get(is_front_polity=True)
            frontpolity.members.add(user)
        except Polity.DoesNotExist:
            pass

    url = settings.ICEPIRATE['url']

    user_post_data = _icepirate_user_data(user)

    remote_object = json.loads(
        requests.get(
            '%s/member/api/get/ssn/%s' % (url, user.userprofile.verified_ssn),
            params=user_post_data
        ).text
    )

    if settings.DEBUG:
        print('Icepirate GET: %s' % remote_object)

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

        # Ask the member database if the user has consented to receiving
        # email and update user database accordingly.
        if user.userprofile.email_wanted != remote_object['data']['email_wanted']:
            user.userprofile.email_wanted = remote_object['data']['email_wanted']
            user.userprofile.save()

        # FIXME: Figure out why we don't just trust Icepirate here...?
        added = datetime.strptime(
            remote_object['data']['added'], '%Y-%m-%d %H:%M:%S')
        if (not user.userprofile.joined_org
                or added < user.userprofile.joined_org):
            user.userprofile.joined_org = added
            user.userprofile.save()

    else:
        error = remote_object['error']

        if error == 'No such member':
            if create_if_missing:

                # Since we're creating the user in the remote database, we
                # need to provide the initial value for whether the user has
                # consented to receiving email. After this, we will trust that
                # the remote database is always correct and change it on this
                # side during login.
                user_post_data['email_wanted'] = 'true' if user.userprofile.email_wanted else 'false'

                remote_object = json.loads(requests.get('%s/member/api/add/' % url, params=user_post_data).text)

                if settings.DEBUG:
                    print('Icepirate ADD: %s' % remote_object)

                if not remote_object['success']:
                    raise IcePirateException(remote_object['error'])

                add_user_to_front_polity()

            else:
                user.polities.clear()
                user.officers.clear()
