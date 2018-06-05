from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from core.signals import user_verified

from gateway.utils import add_member
from gateway.utils import apply_member_locally
from gateway.utils import get_member
from gateway.utils import response_to_results
from gateway.utils import update_member
from gateway.utils import user_to_member_args


@receiver(user_logged_in)
def login_sync(sender, user, request, **kwargs):
    '''
    When a user logs in, data is retrieved from the remote IcePirate
    membership registry and the local user configured accordingly.
    '''

    # No need for this if IcePirate isn't being used.
    if not hasattr(settings, 'ICEPIRATE'):
        return

    # No point hitting the API if we don't have an SSN.
    if not user.userprofile.verified_ssn:
        return

    success, member, error = get_member(user.userprofile.verified_ssn)

    if success:
        apply_member_locally(member, user)
    elif error == 'No such member' and user.userprofile.verified:
        # This means that something has gone wrong when registering the user
        # as a member on IcePirate's side. We'll try again here.
        success, member, error = add_member(user)
    else:
        # If something went wrong, we'll be on the safe side of things and
        # remove membership from polities until we have confirmation from
        # IcePirate on which polities the user should have access to.
        user.polities.clear()
        user.officers.clear()


@receiver(user_verified)
def verified_sync(sender, user, request, **kwargs):

    # No need for this if IcePirate isn't being used.
    if not hasattr(settings, 'ICEPIRATE'):
        return

    success, member, error = get_member(user.userprofile.verified_ssn)

    # Was the member already registered in the membership registry?
    if success:

        # Have any of these values changed?
        changed = any([
            member['email'] != user.email,
            member['email_wanted'] != user.userprofile.email_wanted,
            member['username'] != user.username
        ])
        if changed:
            # If so, we'll update the member registry, because we've just
            # verified our account here and we'll know this information better
            # than the registry, if they differ.
            success, member, error = update_member(user)

        if success: # Success may have changed since last time we asked.
            apply_member_locally(member, user)

    elif error == 'No such member':
        success, member, error = add_member(user)
        if success:
            apply_member_locally(member, user)
