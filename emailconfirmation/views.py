# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from emailconfirmation.models import EmailConfirmation

from gateway.utils import update_member

def email_confirmation(request, key):
    try:
        con = EmailConfirmation.objects.get(key=key)
    except:
        return redirect('/')

    return_url = ''
    return_name = ''

    if con.action == 'email_change':
        con.user.email = con.data
        con.user.save()

        # Update IcePirate registry, if in use.
        if settings.ICEPIRATE['url']:
            update_member(con.user)

        action_detail = '%s: %s' % (_('Your new email address is'), con.data)
        return_url = '/'
        return_name = _('Main page')

    action_msg = dict(EmailConfirmation.ACTIONS)[con.action]

    # We'll want to remove all confirmations of the same type, from the same
    # user. This is to ensure that previous confirmation links that might have
    # been but not received for whatever reason, are made invalid.
    EmailConfirmation.objects.filter(user=con.user, action=con.action).delete()

    # Clean up expired confirmation requests, since we're here.
    EmailConfirmation.objects.filter(timing_created__lt=timezone.now() - timedelta(days=1)).delete()

    ctx = {
        'action_msg': action_msg,
        'action_detail': action_detail,
        'return_url': return_url,
        'return_name': return_name,
    }
    return render(request, 'emailconfirmation/confirmed.html', ctx)

