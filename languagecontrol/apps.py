# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class LanguageControlConfig(AppConfig):
    name = 'languagecontrol'
    verbose_name = 'LanguageControl for Django'

    def ready(self):
        import languagecontrol.signals
