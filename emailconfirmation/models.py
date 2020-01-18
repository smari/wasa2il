# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import string

from core.django_mdmail import send_mail

from django.conf import settings
from django.db import models
from django.db.models import CASCADE
from django.utils.crypto import get_random_string
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


class EmailConfirmation(models.Model):

    ACTIONS = (
        ('email_change', _('Email change')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='email_confirmations', on_delete=CASCADE)

    key = models.CharField(max_length=40)
    timing_created = models.DateTimeField(auto_now=True)

    action = models.CharField(max_length=30, choices=ACTIONS)
    data = models.CharField(max_length=100, null=True)

    def save(self, send=False, *args, **kwargs):

        if self.key == '':
            # Automatically generate a unique key, but make sure that it isn't
            # already in use.
            key = self.generate_key();
            while EmailConfirmation.objects.filter(key=key).count() > 0:
                key = self.generate_key()
            self.key = key

        super(EmailConfirmation, self).save(*args, **kwargs)

    def generate_key(self):
        random_string = get_random_string(length=32, allowed_chars=string.printable)
        return hashlib.sha1(random_string.encode('utf-8')).hexdigest()

    def send(self, request):
        action_msg = dict(self.ACTIONS)[self.action]

        subject = '%s%s' % (settings.EMAIL_SUBJECT_PREFIX, action_msg)
        confirmation_url =  request.build_absolute_uri(reverse('email_confirmation', args=(self.key,)))
        email = self.data if self.action == 'email_change' else self.user.email

        ctx = {
            'action_msg': action_msg,
            'confirmation_url': confirmation_url,
        }
        body = render_to_string('emailconfirmation/emailconfirmation.md', ctx)

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])
