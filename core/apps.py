from django.apps import AppConfig

from core.django_mdmail import convert_md_templates

class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Wasa2il Core'

    def ready(self):
        import core.signals

        convert_md_templates()
